"""Sonda para monitor externo/cron. Não consulta a API esportiva."""
import argparse
import json
import urllib.request

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_url',help='Ex.: https://seu-dominio.com/api')
    args=parser.parse_args()
    try:
        with urllib.request.urlopen(args.base_url.rstrip('/')+'/ready',timeout=10) as r:
            data=json.load(r)
        if not data.get('ready'):raise ValueError('not ready')
    except Exception:
        print('INDISPONÍVEL: falha na sonda de prontidão.');raise SystemExit(1)
    print('OK: servidor pronto; disponibilidade externa não consultada.')
