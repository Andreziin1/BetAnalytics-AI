"""Entrada ASGI da Vercel. Desenvolvimento tradicional continua em backend.main."""
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

# API primeiro; somente os arquivos compilados ficam públicos.
app.mount('/', StaticFiles(directory=Path(__file__).resolve().parent / 'web_dist',
                           html=True, check_dir=False), name='frontend')
