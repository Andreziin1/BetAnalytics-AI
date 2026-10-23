"""Inicializa frontend e backend juntos; Ctrl+C encerra ambos."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def free_port(port):
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            raise RuntimeError(f'Porta {port} ocupada. Encerre o terminal antigo que usa essa porta e tente novamente.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verifica a configuração sem iniciar servidores.')
    args = parser.parse_args()
    os.chdir(ROOT)
    if os.getenv('VERCEL') == '1':
        raise RuntimeError('Este iniciador é exclusivo para seu computador.')
    python = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        if not python.exists():
            subprocess.run([sys.executable, '-m', 'venv', str(ROOT / '.venv')], check=True)
        return subprocess.call([str(python), str(Path(__file__).resolve()), *sys.argv[1:]])
    dependencies = subprocess.run([sys.executable, '-c', 'import fastapi, uvicorn, requests, dotenv'], capture_output=True)
    if dependencies.returncode:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    from dotenv import dotenv_values
    from backend.config import Settings
    if not (ROOT / '.env').exists():
        shutil.copyfile(ROOT / '.env.example', ROOT / '.env')
    # Neste comando explicitamente local, o arquivo salvo prevalece sobre
    # variáveis herdadas de terminais antigos. O deploy mantém outra política.
    values = dotenv_values(ROOT / '.env', encoding='utf-8-sig', interpolate=False)
    for name, value in values.items():
        if value is not None:
            os.environ[name] = value
    os.environ['APP_ENV'] = 'local'
    settings = Settings.from_env()
    if not settings.api_key:
        raise RuntimeError('Preencha API_KEY no arquivo .env da raiz, salve e execute novamente. A chave nunca é mostrada no terminal.')
    print('Configuração OK: chave reconhecida; ambiente local.', flush=True)
    if args.check:
        return 0
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm:
        raise RuntimeError('Instale Node.js 24 e reabra o terminal.')
    for port in (8000, 5173):
        free_port(port)
    if not (ROOT / 'frontend/node_modules/vite/bin/vite.js').exists():
        subprocess.run([npm, 'ci'], cwd=ROOT / 'frontend', check=True)
    children = []
    try:
        children.append(subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1', '--port', '8000']))
        ready = False
        for _ in range(100):
            if children[0].poll() is not None:
                raise RuntimeError('O backend encerrou ao iniciar. Confira a mensagem acima.')
            try:
                with urlopen('http://127.0.0.1:8000/health', timeout=1) as response:
                    ready = json.load(response).get('api_configured') is True
            except OSError:
                pass
            if ready:
                break
            time.sleep(0.1)
        if not ready:
            raise RuntimeError('O backend não confirmou a configuração da chave.')
        env = dict(os.environ, VITE_API_BASE_URL='/api')
        node = shutil.which('node')
        if not node:
            raise RuntimeError('Node.js não encontrado.')
        children.append(subprocess.Popen([node, 'node_modules/vite/bin/vite.js', '--port', '5173', '--strictPort'], cwd=ROOT / 'frontend', env=env))
        print('\nAbra http://127.0.0.1:5173 — Ctrl+C encerra os dois serviços.\n', flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.3)
        raise RuntimeError('Um dos serviços encerrou. Confira a mensagem acima.')
    except KeyboardInterrupt:
        print('\nEncerrando BetAnalytics...')
        return 0
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Não foi possível iniciar: {error}', file=sys.stderr)
        raise SystemExit(1)
