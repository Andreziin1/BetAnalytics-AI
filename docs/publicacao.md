# Publicar na Vercel — BetAnalytics 1.4

## Configuração entregue
Um projeto Vercel contém o backend Python/FastAPI e o frontend React já compilado. Nenhum Docker, Caddy ou servidor separado é necessário para esta configuração.

- `app.py`: entrada FastAPI reconhecida pela Vercel; monta o backend em `/api`.
- `vercel.json`: preset FastAPI, comando de build, duração de função, exclusões e cabeçalhos.
- `.python-version`: Python 3.12; `package.json` da raiz: Node 24.
- `scripts/build_vercel.py`: instala dependências do frontend, compila e copia o resultado para `public/`.
- `public/`: gerado no build e servido pela CDN. Não editar nem versionar.
- `frontend/src/api.js`: usa `/api`, na mesma origem. Não precisa de URL de outro backend.

## 1. Preparar o repositório
Extraia o ZIP. Copie os arquivos para o repositório preservando `.git` e seu `.env` local. Remova os arquivos antigos de Docker/Caddy se estiver atualizando uma pasta existente: `compose.yaml`, `.dockerignore` e a pasta `deploy/`. A simples extração do ZIP não remove arquivos antigos.

O diretório escolhido como raiz do projeto deve conter `app.py`, `vercel.json`, `requirements.txt`, `package.json`, `backend/` e `frontend/`. Não selecione apenas a pasta frontend como Root Directory.

O `.gitignore` e o `.vercelignore` excluem credenciais, ambientes virtuais e dependências geradas. Nunca faça commit do `.env`.

## 2. Criar os códigos individuais de acesso
Na sua máquina, execute na raiz:
```sh
python scripts/create_access.py andre
```
Guarde o código privado para acessar a aplicação. Copie o objeto JSON usuário/hash exibido pelo script para a variável ACCESS_TOKEN_HASHES da Vercel. Não coloque o código em repositório, README ou variável VITE_. Para vários usuários, combine os pares em um objeto JSON.

API_KEY é a chave da football-data.org; código de acesso é outra credencial, gerada pelo script. Não confundir.

## 3. Importar na Vercel
Importe seu repositório Git e configure:

| Campo | Valor |
| --- | --- |
| Framework Preset | FastAPI |
| Root Directory | Raiz que contém app.py e vercel.json |
| Build Command | `python scripts/build_vercel.py` (já definido no arquivo) |
| Install Command | Padrão do preset; não substituir por npm install |
| Output Directory | Padrão do preset; não definir frontend/dist |
| Node.js Version | 24.x |
| Python | 3.12, via .python-version |

O build Python usa `requirements.txt`. O comando de build instala e compila o frontend com `npm ci` e `npm run build` dentro de frontend. Não configure dois projetos ou um proxy para outro servidor.

## 4. Variáveis de ambiente
Cadastre antes do primeiro deploy, tanto em Production quanto em Preview quando utilizar previews:

| Variável | Valor |
| --- | --- |
| API_KEY | Sua chave real da football-data.org |
| APP_ENV | `production` |
| ACCESS_TOKEN_HASHES | Objeto JSON gerado pelo script, sem aspas externas adicionais |
| CACHE_TTL_SECONDS | `300` (opcional) |
| API_REQUESTS_PER_MINUTE | `10` ou o limite do seu plano (opcional) |
| HISTORY_DAYS | `730` (opcional) |
| CLIENT_REQUESTS_PER_MINUTE | `120` (opcional) |
| USER_REQUESTS_PER_MINUTE | `30` (opcional) |

Não crie uma variável VITE_API_KEY. Não precisa definir VITE_API_BASE_URL; o padrão já é `/api`. Remova eventual valor antigo que aponte para localhost. CORS_ORIGINS só precisa ser alterado se você deliberadamente usar outro domínio para consumir a API; o frontend deste projeto usa a mesma origem.

Na Vercel, `VERCEL=1` é definido pela plataforma. O código exige produção e credenciais nesses deployments, inclusive Preview. Não defina VERCEL=1 no desenvolvimento local.

## 5. Deploy e conferência
Clique em Deploy. A URL `*.vercel.app` é suficiente; domínio próprio é opcional. HTTPS é responsabilidade da Vercel.

Depois do deploy:
1. Abra `/api/health`: deve retornar 200 e access_required=true.
2. Abra `/api/ready`: deve retornar 200. Essa rota verifica configuração, não autentica na API esportiva.
3. Abra `/`: deve exibir a interface, não JSON.
4. Informe seu código de acesso e busque jogos de uma liga.
5. Abra uma análise e confira tamanho das amostras e avisos.
6. Consulte os Runtime Logs da função para diagnosticar falhas. A aplicação registra status, rota e duração, sem tokens ou query strings.

A sonda opcional funciona com:
```sh
python scripts/check_health.py https://SEU-PROJETO.vercel.app/api
```
Se Deployment Protection estiver habilitado para um Preview, o monitor pode receber bloqueio da Vercel; abra o Preview autenticado ou configure acesso de monitor conforme sua conta.

## Limites específicos de serverless
- A função está configurada com maxDuration=180 segundos. A espera do frontend é 190 segundos para permitir receber o erro da plataforma. Ative/mantenha Fluid Compute e confirme compatibilidade com seu plano nas configurações da Vercel. Não há garantia de conclusão se a fonte ou a fila de requisições estiverem lentas.
- Cache, cooldown, quotas e /metrics ficam em memória por instância. Cold starts, novos deployments e escala automática reiniciam/dividem esses estados.
- Portanto, API_REQUESTS_PER_MINUTE é uma proteção preventiva por instância, não uma quota global garantida entre todas as funções. O fornecedor continua impondo o limite real da chave. Os limites por usuário/IP também são locais à instância.
- A autenticação funciona em todas as instâncias por usar as mesmas variáveis de ambiente. Restrinja inicialmente o acesso a poucos usuários. Para tráfego concorrente ou garantia de quotas globais, é necessário implementar cache/limite distribuídos (por exemplo, Redis); esse serviço não foi criado nem configurado.
- /metrics é um retrato da instância atendente, não um painel agregado. Use Observability/Runtime Logs da Vercel para acompanhar o deployment.
- Não existem processos permanentes, armazenamento durável local ou cron instalado. Alertas externos dependem de configuração na conta/plataforma de monitoramento.

## Atualizações e revogação
Faça novo deploy após alterar variáveis ou retirar um usuário de ACCESS_TOKEN_HASHES. Deployments antigos podem continuar acessíveis com suas configurações anteriores: proteja ou remova os deployments antigos na Vercel quando revogar acesso. Os arquivos estáticos podem ser públicos; a API é protegida por código.

## O que foi e não foi validado
O build local, a geração de public/, o contrato ASGI com prefixo /api, autenticação e testes foram validados. O projeto não foi publicado na conta Vercel nesta tarefa; a integração final com CDN, runtime, variáveis e limites da conta deve ser verificada no primeiro Preview.

## Referências oficiais
- https://vercel.com/docs/frameworks/backend/fastapi
- https://vercel.com/docs/functions/runtimes/python
- https://vercel.com/docs/functions/configuring-functions/duration
- https://vercel.com/docs/headers/request-headers
