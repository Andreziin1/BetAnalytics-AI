"""Regressões de configuração; todas as credenciais abaixo são sintéticas."""
import os
import pytest
import backend.config as config


@pytest.fixture
def env_file(tmp_path, monkeypatch):
    path = tmp_path / '.env'
    monkeypatch.setattr(config, 'ENV_FILE', path)
    for name in ('API_KEY', 'APP_ENV', 'VERCEL', 'ACCESS_TOKEN_HASHES'):
        monkeypatch.delenv(name, raising=False)
    return path


def test_utf8_bom(env_file):
    env_file.write_text('API_KEY=synthetic-token\nAPP_ENV=local\n', encoding='utf-8-sig')
    assert config.Settings.from_env().api_key == 'synthetic-token'


def test_saved_file_is_reread_without_polluting_environment(env_file):
    env_file.write_text('API_KEY=synthetic-first\n')
    assert config.Settings.from_env().api_key == 'synthetic-first'
    assert 'API_KEY' not in os.environ
    env_file.write_text('API_KEY=synthetic-second\n')
    assert config.Settings.from_env().api_key == 'synthetic-second'


def test_host_environment_has_precedence(env_file, monkeypatch):
    env_file.write_text('API_KEY=synthetic-file\n')
    monkeypatch.setenv('API_KEY', 'synthetic-host')
    assert config.Settings.from_env().api_key == 'synthetic-host'


def test_vercel_never_loads_local_file(env_file, monkeypatch):
    env_file.write_text('APP_ENV=local\nAPI_KEY=synthetic-file\n')
    monkeypatch.setenv('VERCEL', '1')
    with pytest.raises(ValueError, match='Produção exige'):
        config.Settings.from_env()
