"""Build React e preparação dos arquivos públicos para o preset FastAPI."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    npm = shutil.which('npm')
    if not npm:
        raise SystemExit('Node.js/npm não encontrado. Instale Node 24 para gerar o frontend.')
    frontend = ROOT / 'frontend'
    subprocess.run([npm, 'ci', '--include=dev'], cwd=frontend, check=True)
    subprocess.run([npm, 'run', 'build'], cwd=frontend, check=True)
    required = ['index.html', 'favicon.svg',
                'fonts/dm-sans-latin-wght-normal.woff2',
                'fonts/manrope-latin-wght-normal.woff2']
    for name in required:
        if not (frontend / 'dist' / name).is_file():
            raise SystemExit(f'Build incompleto: falta {name}. Confira frontend/public no GitHub.')
    output = ROOT / 'web_dist'
    marker = output / '.betanalytics-build'
    if output.exists():
        if not marker.is_file():
            raise SystemExit('web_dist/ já existe e não foi gerado por este script. Preserve seu conteúdo antes do build.')
        shutil.rmtree(output)
    shutil.copytree(frontend / 'dist', output)
    marker.write_text('Diretório gerado por scripts/build_vercel.py. Não editar.\n')
    print('Frontend preparado em web_dist/; o backend será publicado a partir de app.py.')

if __name__ == '__main__':
    main()
