# BetAnalytics IA

Análise descritiva pré-jogo de futebol em Python/FastAPI. Nesta fase o backend é implementado e testado; o frontend React/Vite é uma estrutura inicial executável. Não há IA, previsões, recomendações ou outros esportes implementados.

## Iniciar no Windows

Abra o terminal na raiz extraída, onde estão requirements.txt e backend.
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```
Edite .env e coloque sua chave football-data.org em API_KEY. Se já tem .env, preserve-o e confira o valor de API_KEY: textos como `sua_chave` são exemplos, não credenciais válidas. A chave fica no `.env` da raiz, ao lado de requirements.txt. Depois de alterar a chave, pare o Uvicorn com Ctrl+C e inicie novamente.
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```
API: http://127.0.0.1:8000 · documentação interativa: http://127.0.0.1:8000/docs

## Linux ou macOS
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python -m uvicorn backend.main:app --reload
```
Requer Python 3.11+; validado em Python 3.12. Configure .env antes de consultar dados.
Execute sempre a partir da raiz; o comando antigo dentro de backend foi substituído.

## Frontend nesta fase
Em outro terminal:
```sh
cd frontend
npm ci
npm run dev
```
Requer Node 22.12+ ou 24. Abra no Chrome o endereço mostrado pelo Vite e mantenha os dois terminais abertos.
O frontend usa `/api`, encaminhado pelo Vite para `http://127.0.0.1:8000`.
Isso funciona mesmo quando o Vite usa 5174 porque 5173 já está ocupada.
Se existir `frontend/.env`, configure `VITE_API_BASE_URL=/api` e reinicie o Vite.
Não é necessário criar esse arquivo para uso local. Nunca coloque a chave esportiva no frontend.
A tela permite selecionar campeonato e período e listar partidas reais. Consulte frontend/README.md.

## Endpoints
| Rota GET | Finalidade |
| --- | --- |
| /health | Processo ativo e indicação de chave configurada; não verifica autenticação externa |
| /competitions | Códigos configurados, sem promessa de cobertura da assinatura |
| /matches?days=7&competitions=PL,BSA | Jogos futuros dentro de sete datas UTC, incluindo hoje |
| /matches/{id}/analysis | Histórico, comparação, H2H, metadados e avisos |

/matches retorna um objeto com matches, discarded, timezone e days.
A análise retorna home_team_analysis, away_team_analysis e head_to_head.
head_to_head agora é objeto com matches e resumo. Equipes da partida são objetos com id e name.
Essas mudanças de contrato estão documentadas em docs/api.md.

## Regras
- Até dez jogos válidos por time e cinco H2H, em ordem decrescente de data.
- Jogos finalizados, com equipes, ID, data com fuso, competição e placar válidos.
- Corte: menor entre o horário atual e o início da partida-alvo; alvo nunca participa.
- Competições oficiais combinadas; amistosos/tipos desconhecidos descartados. A competição aparece em cada linha.
- Placar de tempo regulamentar: fullTime somente para duration=REGULAR; nos demais casos exige regularTime explícito.
- Ausência de dados resulta em null nas médias, percentuais e gols, não em zero.
- Duplicatas iguais contam uma vez; IDs com versões válidas conflitantes são excluídos.
- Histórico limitado a HISTORY_DAYS (730 por padrão), até 500 candidatos por equipe e 100 H2H.
- Amostras insuficientes, falhas parciais, limites e descartes são informados.
- Subgrupos casa/fora usam a amostra de dez, não dez jogos adicionais em cada condição.

O corte por data não reconstrói a versão histórica da base nem prova quando um resultado ficou disponível. Não usar esta versão como backtest de modelo. A API externa pode corrigir dados retroativamente.

## Testes
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
No Linux: .venv/bin/python -m pytest -q.
Os testes usam dados sintéticos identificados exclusivamente como fixtures. Não consomem a chave real.

## Configuração e operação
CACHE_TTL_SECONDS: 300; cache em memória limitado a 256 respostas.
API_REQUESTS_PER_MINUTE: 10; ajuste conforme seu plano. É um limite preventivo local, não confirmação de franquia.
HISTORY_DAYS: 730; janela explícita, não histórico ilimitado.
CORS_ORIGINS: origens locais explícitas por padrão; configurar a origem real quando houver deploy.
Uma instância/worker por chave nesta fase: cache e limite não são compartilhados entre processos.
Sem repetição automática em 429, evitando aumentar consumo; Retry-After orienta o cliente.
Timeout externo de conexão/leitura: 20/20 segundos por chamada. Sem redirecionamento da chave.
Sem autenticação de usuário: entrega para execução local; publicação pública requer proteção e quotas por usuário.
A chave permanece apenas no backend. O ZIP de entrega não contém .env, .git, caches ou node_modules.

