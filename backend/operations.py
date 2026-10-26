"""Proteção e observabilidade locais ao processo. Nenhuma credencial nos logs."""
from collections import OrderedDict, deque, Counter
from hashlib import sha256
from threading import Lock
from time import monotonic
from uuid import uuid4
from ipaddress import ip_address
import json
import logging

from fastapi.responses import JSONResponse

logger = logging.getLogger('betanalytics.requests')

class Operations:
    def __init__(self, settings, clock=monotonic):
        self.settings = settings
        self.clock = clock
        self.lock = Lock()
        self.buckets = OrderedDict()
        self.started = clock()
        self.counts = Counter()
        self.total_ms = 0

    def consume(self, key, limit):
        with self.lock:
            now = self.clock()
            # Não guardar identidades ou IPs nos buckets.
            key = sha256(key.encode()).hexdigest()
            bucket = self.buckets.setdefault(key, deque())
            self.buckets.move_to_end(key)
            while bucket and now - bucket[0] >= 60:
                bucket.popleft()
            if len(bucket) >= limit:
                return max(1, int(60 - (now - bucket[0])) + 1)
            bucket.append(now)
            while len(self.buckets) > 10000:
                self.buckets.popitem(last=False)
            return None

    def snapshot(self):
        with self.lock:
            total = sum(self.counts.values())
            return {'uptime_seconds': round(self.clock()-self.started), 'requests':total,
                    'statuses':dict(self.counts), 'average_response_ms':round(self.total_ms/total,2) if total else 0,
                    'scope':'single_process'}

    async def middleware(self, request, call_next):
        start = self.clock()
        request_id = uuid4().hex
        path = request.url.path
        # /api é o prefixo de montagem na Vercel, não uma rota do backend.
        root_path = request.scope.get('root_path', '').rstrip('/')
        if root_path and (path == root_path or path.startswith(root_path + '/')):
            path = path[len(root_path):] or '/' 
        def error(status, code, message, retry=None):
            headers = {'Retry-After':str(retry)} if retry else {}
            return JSONResponse(status_code=status, headers=headers, content={'error':{'code':code,'message':message}})
        response = None
        public = path in {'/health','/ready'}
        # Preflight é tratado pelo middleware CORS externo.
        if not public and request.method != 'OPTIONS':
            ip = request.client.host if request.client else 'unknown'
            if self.settings.on_vercel:
                # A borda da Vercel substitui X-Forwarded-For; não confiar fora dela.
                forwarded = request.headers.get('x-forwarded-for', '').split(',')[0].strip()
                try:
                    ip = str(ip_address(forwarded))
                except ValueError:
                    pass
            retry = self.consume('ip:'+ip, self.settings.client_requests_per_minute)
            if retry:
                response = error(429,'client_rate_limit','Muitas consultas. Aguarde para tentar novamente.',retry)
        if response is None:
            try:
                response = await call_next(request)
            except Exception as exc:
                logger.error(json.dumps({'event':'internal_error','request_id':request_id,'type':type(exc).__name__}))
                response = error(500,'internal_error','Falha interna ao processar a solicitação.')
        elapsed = (self.clock()-start)*1000
        with self.lock:
            self.counts[str(response.status_code)] += 1
            self.total_ms += elapsed
        route = request.scope.get('route')
        logger.info(json.dumps({'event':'http_request','request_id':request_id,
                               'route':getattr(route,'path','unmatched'),'method':request.method,
                               'status':response.status_code,'duration_ms':round(elapsed,2)}))
        response.headers['X-Request-ID'] = request_id
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-store'
        return response
