"""Entrada ASGI da Vercel. Desenvolvimento tradicional continua em backend.main."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from backend.main import app as backend_app

# Logs próprios em JSON no stdout, visíveis nos Runtime Logs da Vercel.
logger = logging.getLogger('betanalytics')
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

@asynccontextmanager
async def lifespan(app):
    # Lifespan de aplicações montadas não é executado automaticamente pelo ASGI.
    async with backend_app.router.lifespan_context(backend_app):
        yield

app = FastAPI(title='BetAnalytics', docs_url=None, redoc_url=None,
              openapi_url=None, lifespan=lifespan)
app.mount('/api', backend_app)

@app.get('/', include_in_schema=False)
def frontend():
    # A regra de plataforma serve public/index.html pela CDN.
    return RedirectResponse('/index.html', status_code=307)
