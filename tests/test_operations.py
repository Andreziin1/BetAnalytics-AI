from hashlib import sha256
import json
import logging
from fastapi.testclient import TestClient
import pytest
from backend.main import create_app
from backend.config import Settings
from backend.operations import Operations

TOKEN = 'synthetic-test-access-code-not-a-real-secret'
USERS = (('tester', sha256(TOKEN.encode()).hexdigest()),)
AUTH = {'Authorization':f'Bearer {TOKEN}'}

def test_protected_api_and_public_health():
    with TestClient(create_app(Settings(access_token_hashes=USERS))) as http:
        assert http.get('/health').status_code == 200
        assert http.get('/competitions').status_code == 401
        assert http.get('/competitions',headers={'Authorization':'Bearer wrong'}).status_code == 401
        assert http.get('/competitions',headers=AUTH).status_code == 200
        assert http.get('/metrics').status_code == 401
        metrics = http.get('/metrics',headers=AUTH).json()
        assert metrics['requests'] >= 5
        assert TOKEN not in json.dumps(metrics)

def test_user_limit_and_recovery():
    ops=Operations(Settings(access_token_hashes=USERS,user_requests_per_minute=1))
    clock=[0];ops.clock=lambda:clock[0]
    assert ops.consume('user:tester',1) is None
    assert ops.consume('user:tester',1)==61
    clock[0]=61
    assert ops.consume('user:tester',1) is None

def test_http_limits_do_not_call_provider():
    with TestClient(create_app(Settings(access_token_hashes=USERS,user_requests_per_minute=1))) as http:
        assert http.get('/competitions',headers=AUTH).status_code==200
        r=http.get('/competitions',headers=AUTH)
        assert r.status_code==429 and int(r.headers['retry-after'])>0

def test_invalid_auth_has_ip_limit():
    with TestClient(create_app(Settings(access_token_hashes=USERS,client_requests_per_minute=1))) as http:
        assert http.get('/competitions').status_code==401
        assert http.get('/competitions').status_code==429
        assert http.get('/health').status_code==200

def test_production_refuses_missing_credentials():
    with pytest.raises(ValueError):create_app(Settings(environment='production'))

def test_production_hides_docs():
    with TestClient(create_app(Settings(environment='production',api_key='synthetic',access_token_hashes=USERS))) as http:
        assert http.get('/openapi.json',headers=AUTH).status_code==404
        assert http.get('/ready').status_code==200
        assert http.get('/ready').json()['provider_checked'] is False

def test_no_secrets_in_access_logs(caplog):
    with caplog.at_level(logging.INFO,logger='betanalytics.requests'):
        with TestClient(create_app(Settings(access_token_hashes=USERS))) as http:
            r=http.get('/competitions?secret=synthetic-hidden',headers=AUTH)
    assert 'http_request' in caplog.text
    assert TOKEN not in caplog.text
    assert 'synthetic-hidden' not in caplog.text
    assert r.headers['x-request-id']
    assert r.headers['cache-control']=='no-store'

def test_cors_wraps_auth_failures():
    with TestClient(create_app(Settings(access_token_hashes=USERS))) as http:
        r=http.get('/competitions',headers={'Origin':'http://localhost:5173'})
        assert r.status_code==401
        assert r.headers['access-control-allow-origin']=='http://localhost:5173'
        r=http.options('/competitions',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'Authorization'})
        assert r.status_code==200

@pytest.mark.parametrize('value',['[]','invalid','{"user":"plaintext"}'])
def test_invalid_hash_configuration(monkeypatch,value):
    monkeypatch.setenv('ACCESS_TOKEN_HASHES',value)
    with pytest.raises(ValueError,match='ACCESS_TOKEN_HASHES'):Settings.from_env()

def test_readiness_without_api_key():
    with TestClient(create_app(Settings())) as http:
        assert http.get('/ready').status_code==503
