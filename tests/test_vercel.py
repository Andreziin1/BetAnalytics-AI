"""Contrato ASGI de publicação, sem depender de conta ou API externa."""
import importlib
import json
from pathlib import Path
from hashlib import sha256
from fastapi.testclient import TestClient
import pytest
from backend.config import Settings
from backend.main import create_app

ROOT = Path(__file__).resolve().parents[1]

def mounted(monkeypatch, tmp_path):
    import backend.main as backend
    token = 'synthetic-vercel-access'
    app = create_app(Settings(environment='production',api_key='synthetic',
                              access_token_hashes=(('test',sha256(token.encode()).hexdigest()),)))
    monkeypatch.setattr(backend, 'app', app)
    import app as entry
    application = importlib.reload(entry).app
    # Cada teste usa uma raiz isolada: não depende de npm para testar a API.
    from fastapi.staticfiles import StaticFiles
    (tmp_path / 'index.html').write_text('<!doctype html><title>BetAnalytics</title>')
    application.routes[-1].app = StaticFiles(directory=tmp_path, html=True)
    return application, {'Authorization':'Bearer '+token}

def test_vercel_health_and_readiness_public_under_api(monkeypatch, tmp_path):
    app, auth = mounted(monkeypatch, tmp_path)
    with TestClient(app) as http:
        assert http.get('/api/health').status_code == 200
        assert http.get('/api/ready').status_code == 200
        assert http.get('/api/competitions').status_code == 401
        assert http.get('/api/competitions',headers=auth).status_code == 200
        assert http.get('/api/metrics',headers=auth).status_code == 200
        assert http.get('/api/openapi.json',headers=auth).status_code == 404
        assert http.get('/health').status_code == 404


def test_vercel_route_validation_still_applies(monkeypatch, tmp_path):
    app, auth = mounted(monkeypatch, tmp_path)
    with TestClient(app) as http:
        r=http.get('/api/matches?days=99',headers=auth)
        assert r.status_code == 422
        assert r.json()['error']['code'] == 'validation_error'
        assert http.get('/api/matches/0/analysis',headers=auth).status_code == 422

@pytest.mark.parametrize('value',['local',''])
def test_vercel_cannot_disable_production(monkeypatch,value):
    monkeypatch.setenv('VERCEL','1');monkeypatch.setenv('APP_ENV',value)
    with pytest.raises(ValueError,match='APP_ENV=production'):Settings.from_env()

def test_vercel_defaults_to_production(monkeypatch):
    monkeypatch.setenv('VERCEL','1');monkeypatch.delenv('APP_ENV',raising=False)
    monkeypatch.setenv('API_KEY','synthetic-token')
    monkeypatch.setenv('ACCESS_TOKEN_HASHES',json.dumps({'test':sha256(b'synthetic-access').hexdigest()}))
    assert Settings.from_env().environment == 'production'

def test_platform_config_does_not_rewrite_api_to_frontend():
    config=json.loads((ROOT/'vercel.json').read_text())
    assert config['framework']=='fastapi'
    assert not config.get('rewrites')
    assert 'app.py' in config['functions']
    assert not (ROOT/'compose.yaml').exists()
    assert not (ROOT/'deploy').exists()

@pytest.mark.parametrize('on_vercel,second_status',[(True,200),(False,429)])
def test_forwarded_ip_trusted_only_on_vercel(on_vercel,second_status):
    app=create_app(Settings(on_vercel=on_vercel,client_requests_per_minute=1))
    with TestClient(app) as http:
        assert http.get('/competitions',headers={'X-Forwarded-For':'192.0.2.1'}).status_code==200
        assert http.get('/competitions',headers={'X-Forwarded-For':'192.0.2.2'}).status_code==second_status


def test_built_frontend_and_api_share_the_production_entrypoint():
    import re
    import app as entry
    if not (ROOT / 'web_dist/index.html').exists():
        pytest.skip('Execute python scripts/build_vercel.py para validar o build real.')
    application = importlib.reload(entry).app
    with TestClient(application) as http:
        response = http.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']
        assert 'id="root"' in response.text
        assets = re.findall(r'(?:src|href)="(/assets/[^"]+)"', response.text)
        assert len(assets) >= 2
        for asset in assets:
            result = http.get(asset)
            assert result.status_code == 200
            assert 'text/html' not in result.headers['content-type']
        for font in ['dm-sans', 'manrope']:
            result = http.get(f'/fonts/{font}-latin-wght-normal.woff2')
            assert result.status_code == 200
            assert result.content[:4] == b'wOF2'
        assert http.get('/favicon.svg').status_code == 200
        assert http.get('/api/health').json()['status'] == 'online'
        assert http.get('/index.html').status_code == 200
        for path in ['/app.py', '/.env', '/backend/config.py', '/assets/missing.js', '/%2e%2e/app.py']:
            assert http.get(path).status_code == 404
