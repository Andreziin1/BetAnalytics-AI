import logging
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.config import Settings
from backend.operations import Operations

def test_api_is_public_and_reports_metrics():
    with TestClient(create_app(Settings())) as http:
        assert http.get('/health').status_code == 200
        assert http.get('/competitions').status_code == 200
        metrics = http.get('/metrics').json()
        assert metrics['requests'] >= 2

def test_client_limit_and_recovery():
    ops=Operations(Settings(client_requests_per_minute=1))
    clock=[0];ops.clock=lambda:clock[0]
    assert ops.consume('ip:192.0.2.1',1) is None
    assert ops.consume('ip:192.0.2.1',1)==61
    clock[0]=61
    assert ops.consume('ip:192.0.2.1',1) is None

def test_http_limit_applies_to_public_requests():
    with TestClient(create_app(Settings(client_requests_per_minute=1))) as http:
        assert http.get('/competitions').status_code==200
        r=http.get('/competitions')
        assert r.status_code==429 and int(r.headers['retry-after'])>0
        assert http.get('/health').status_code==200

def test_production_requires_only_provider_key():
    try:
        create_app(Settings(environment='production'))
    except ValueError as error:
        assert 'API_KEY' in str(error)
    else:
        raise AssertionError('Produção sem API_KEY deveria falhar')

def test_production_hides_docs_and_is_public():
    with TestClient(create_app(Settings(environment='production',api_key='synthetic'))) as http:
        assert http.get('/openapi.json').status_code==404
        assert http.get('/competitions').status_code==200
        assert http.get('/ready').status_code==200
        assert http.get('/health').json()['public_access'] is True

def test_no_query_values_in_access_logs(caplog):
    with caplog.at_level(logging.INFO,logger='betanalytics.requests'):
        with TestClient(create_app(Settings())) as http:
            r=http.get('/competitions?private=synthetic-hidden')
    assert 'http_request' in caplog.text
    assert 'synthetic-hidden' not in caplog.text
    assert r.headers['x-request-id']
    assert r.headers['cache-control']=='no-store'

def test_cors_wraps_public_response():
    with TestClient(create_app(Settings())) as http:
        r=http.get('/competitions',headers={'Origin':'http://localhost:5173'})
        assert r.status_code==200
        assert r.headers['access-control-allow-origin']=='http://localhost:5173'
        r=http.options('/competitions',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'GET'})
        assert r.status_code==200

def test_readiness_without_api_key():
    with TestClient(create_app(Settings())) as http:
        assert http.get('/ready').status_code==503
