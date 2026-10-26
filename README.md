# BetAnalytics

Análise descritiva pré-jogo de futebol em Python/FastAPI. Backend implementado com frontend React/Vite integrado: busca, comparação de equipes, históricos, confrontos diretos e avisos. Não há IA, previsões, recomendações ou outros esportes implementados.

## Iniciar no Windows

### Forma recomendada: um único terminal

Preserve seu `.env` da raiz ao atualizar os arquivos. Ele deve conter sua chave real em `API_KEY`; `APP_ENV=local` é opcional no iniciador abaixo. O ZIP de entrega não inclui a credencial.

Na raiz, execute:

```powershell
.\iniciar.cmd
```

Ou dê dois cliques em `iniciar.cmd`. Requer Python 3.11+ e Node.js 24 instalados. O iniciador cria `.venv` se necessário, instala dependências ausentes e abre os dois servidores. Não é necessário ativar o ambiente virtual nem alterar a política do PowerShell. Abra http://127.0.0.1:5173 e mantenha esse terminal aberto. Ctrl+C encerra ambos.

Este iniciador usa o `.env` salvo com prioridade sobre valores antigos herdados pelo terminal e fixa o proxy em `/api`. Se faltar a chave, cria um `.env` de exemplo e informa o que preencher. Se as portas 8000 ou 5173 estiverem ocupadas, interrompe sem encerrar processos alheios. Feche o servidor antigo indicado e execute novamente. Após editar o `.env`, reinicie o iniciador.

Para verificar a configuração sem mostrar a chave:

```powershell
py scripts/start_local.py --check
```

### Forma manual: dois terminais

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
[ -f .env ] || cp .env.example .env
.venv/bin/python -m uvicorn backend.main:app --reload
```
Requer Python 3.11+; validado em Python 3.12. Configure .env antes de consultar dados.
Execute sempre a partir da raiz; o comando antigo dentro de backend foi substituído.

## Frontend
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
A tela permite selecionar campeonato e período, listar partidas e abrir a análise visual em uma área dedicada.

## Endpoints
| Rota GET | Finalidade |
| --- | --- |
| /health | Processo ativo e indicação de chave configurada; não verifica autenticação externa |
| /competitions | Códigos configurados, sem promessa de cobertura da assinatura |
| /matches?days=7&competitions=PL,BSA | Jogos futuros dentro de sete datas UTC, incluindo hoje |
| /matches/{id}/analysis | Histórico, comparação, H2H, metadados e avisos |

/matches retorna matches, discarded, timezone, days, warnings, partial e retrieved_at por campeonato. Falhas isoladas preservam campeonatos disponíveis; falha em todos retorna erro HTTP.
A análise retorna home_team_analysis, away_team_analysis e head_to_head.
head_to_head agora é objeto com matches e resumo. Equipes da partida são objetos com id e name.
Os contratos usados pelo frontend são definidos pelos endpoints FastAPI e validados pela suíte de testes.

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
Cache, quotas e métricas são locais à instância; na Vercel a escala automática não compartilha esses estados.
Sem repetição automática em 429; novas chamadas externas respeitam o Retry-After do fornecedor. Respostas ainda válidas em cache continuam disponíveis.
Timeout externo de conexão/leitura: 20/20 segundos por chamada. Sem redirecionamento da chave.
O site é público. As consultas são limitadas por IP para reduzir abuso; a chave esportiva permanece somente no backend.
A chave permanece apenas no backend. O ZIP de entrega não contém .env, .git, caches ou node_modules.


## Revisão de 23/10/2026
Os requisitos funcionais e não funcionais estão em `docs/requisitos.md`.
No frontend, `npm test` executa o teste automatizado de interface em DOM simulado.
O BPMN atualizado está em `docs/BPMN.png`, `docs/BPMN.svg` e `docs/BPMN.bpmn` (editável em ferramentas BPMN).
Ao atualizar uma pasta existente, mantenha seu `.env` local e reinstale as dependências com `npm ci`. Não copie `node_modules` ou ambientes virtuais entre computadores.

## Funcionalidades da aplicação
- Filtros locais por time (ignorando acentos) e data de Brasília, ordenação e limpeza.
- Gráficos de V/E/D e médias de gols, detalhes em casa/fora e retorno com foco ao jogo selecionado.
- Escudos ausentes/quebrados substituídos por iniciais.
- Interface e API identificadas como BetAnalytics, sem alegar uso de IA.
- Acesso público, limite por IP, logs estruturados e métricas.
- Implantação preparada para Vercel, com frontend e FastAPI no mesmo projeto; domínio próprio é opcional.

## Testes adicionais
```sh
cd frontend
npx playwright install chromium
npm run test:e2e
```
O teste inicia seu próprio Vite na porta 5179 e usa dados sintéticos. Testa os fluxos principais nas telas de 1440 e 390 pixels. Pode usar E2E_BASE_URL para um frontend já iniciado.

Na raiz, para testar sua integração real (consome até cinco chamadas):
```sh
python scripts/check_live.py --competition PL
```
Usa o `.env` local. Respeite a quota antes de repetir ou testar outra liga.

## Publicar na Vercel (versão 1.4)
Use **Framework Preset: FastAPI** e a raiz que contém `app.py` e `vercel.json`, nunca apenas `frontend/`. Não configure Output Directory como frontend/dist. O build é `python scripts/build_vercel.py`.
Cadastre `API_KEY` e `APP_ENV=production` nas variáveis de ambiente antes do deploy. `ACCESS_TOKEN_HASHES` não é mais usado e pode ser removido da Vercel. Na Vercel, mantenha a raiz do projeto como diretório de publicação, use o preset FastAPI e não configure manualmente um Output Directory.
Os arquivos Docker/Caddy foram removidos. Se atualizar uma pasta existente, remova manualmente compose.yaml, .dockerignore e deploy/; extrair o ZIP não remove arquivos antigos.

### Correção da publicação do frontend
O build gera `web_dist/` e verifica HTML, favicon e fontes. `app.py` monta esse
diretório com `StaticFiles` após `/api`; a função inclui `web_dist/**`, permitindo
servir HTML, CSS, JavaScript e fontes também pelo ASGI. Não há redirecionamento
para um arquivo sem rota. `frontend/public/` contém fontes e favicon e deve estar
versionado; somente `/public/` e `/web_dist/` na raiz são artefatos gerados.

Depois de substituir os arquivos na pasta local existente (preservando `.git`):

```powershell
git add .
git commit -m "Libera acesso publico ao BetAnalytics"
git push origin main
```

Aguarde o novo deploy e confira `/` (HTML), `/api/health` (JSON) e uma análise
sem solicitar código de acesso. O status Ready sozinho não valida o site.


Indicadores por equipe: ambas marcam e jogos sem sofrer gols (quantidade e percentual da amostra válida), além de média de gols totais (marcados + sofridos). Amostra vazia retorna indisponível. Frequências não representam previsões.


Competições disponíveis (plano gratuito): Premier League (PL), La Liga (PD), Serie A italiana (SA), Bundesliga (BL1), Ligue 1 (FL1), Champions League (CL), Primeira Liga (PPL), Brasileirão Série A (BSA), Eredivisie (DED), Championship (ELC), Eurocopa (EC) e Copa do Mundo (WC). Cobertura conferida em 26/10/2026: https://www.football-data.org/coverage. A disponibilidade de partidas e histórico depende do calendário e da fonte. O seletor separa ligas e copas; a barra lateral permite buscar por nome ou código. Cada seleção consulta apenas a competição escolhida.
