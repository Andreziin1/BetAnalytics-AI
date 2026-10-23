"""Gera código aleatório e hash, sem gravar arquivo. Execute localmente."""
import argparse
import hashlib
import json
import re
import secrets

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('user', help='Identificador sem espaços, até 64 caracteres')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.user):
        parser.error('Usuário inválido.')
    token = secrets.token_urlsafe(32)
    print('Código privado de acesso (entregue somente ao usuário):')
    print(token)
    print('Adicione este par ao objeto ACCESS_TOKEN_HASHES do servidor:')
    print(json.dumps({args.user:hashlib.sha256(token.encode()).hexdigest()}))
