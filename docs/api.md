# Contrato REST versão 1.4

Documentação de parâmetros em /docs e /openapi.json.
Datas retornadas em ISO 8601 com fuso UTC. Valores monetários e odds não fazem parte desta API.

## Listagem
GET /matches?days=7&competitions=PL,BSA
days aceita 1 a 30; representa datas UTC incluindo hoje, excluindo partidas cujo horário já passou.
competitions é opcional, separado por vírgulas. Lista permitida em /competitions; acesso efetivo depende da assinatura.
Resposta: matches (lista), discarded (quantidade de registros inválidos), days, timezone, warnings, partial e retrieved_at por campeonato. Uma liga indisponível não apaga as demais. Se todas falharem, retorna o primeiro erro; autenticação inválida interrompe imediatamente.
Cada partida possui id, date, status, competition, home_team e away_team.

## Análise
GET /matches/{match_id}/analysis, identificador inteiro positivo.
match contém identificação e equipes.
home_team_analysis e away_team_analysis contêm:
team_id, team, available, matches_analyzed, sample_complete, wins, draws, losses,
goals_scored, goals_conceded, average_goals_scored, average_goals_conceded,
win_percentage, draw_percentage, loss_percentage, form, last_10, home, away, discarded.
form usa W/D/L; converter para V/E/D na apresentação.
last_10 inclui data, competição, temporada quando disponível, IDs, nomes, placar, venue, goals_for, goals_against e result.
home/away são resumos do subconjunto de jogos selecionados.

head_to_head contém available, matches, matches_analyzed, sample_complete,
home_team_wins, draws, away_team_wins, total_goals, average_total_goals e discarded.
home_team_wins refere-se à equipe mandante da partida-alvo, inclusive quando ela foi visitante no encontro histórico.
metadata contém source, generated_at, retrieved_at por fonte, cutoff, history_days, timezone,
score_basis, form_order, competition_policy, partial e historical_caveat.
retrieved_at conserva o instante da coleta mesmo em cache; generated_at é o instante de geração.
warnings contém objetos code, section, message e retry_after opcional em segundos.
partial=true sinaliza limitações ou dados descartados; não equivale necessariamente à indisponibilidade da API.

## Erros
Envelope: {"error": {"code": "...", "message": "..."}}
422: parâmetros inválidos; pode incluir fields.
404: partida/recurso inexistente.
429: quota local ou externa; Retry-After em segundos.
502: falha de conexão, resposta inválida ou erro do fornecedor.
503: chave ausente/inválida ou recurso não autorizado pela assinatura.
504: timeout externo.
500: falha interna com mensagem genérica.
Uma consulta de análise pode responder 200 com seções disponíveis e warnings; verifique available e matches_analyzed.
Sem dados: médias, gols e percentuais são null. Contagens V/E/D vazias são zero sobre amostra de tamanho zero.

## Mudanças
/matches anteriormente era uma lista direta; agora é um envelope.
match.home_team e away_team anteriormente eram nomes; agora são objetos.
head_to_head anteriormente era uma lista; agora contém matches e agregados.
O frontend desta entrega consome o contrato 1.3 e apresenta as análises na tela.


## Operação e acesso (1.3)
GET /health: estado do processo, api_configured e access_required. Público; não valida a chave no fornecedor.
GET /ready: 200 se a chave está configurada, 503 caso contrário; provider_checked=false. Público.
GET /metrics: contagens por status, uptime, média de duração e scope=single_process.
Quando ACCESS_TOKEN_HASHES contém usuários, todas as rotas exceto /health e /ready exigem Authorization: Bearer <código individual>. Ausência ou código inválido retorna 401, error.code=access_required. Nunca use API_KEY do fornecedor no navegador.
Limites por usuário e IP retornam 429 com Retry-After, códigos user_rate_limit/client_rate_limit. Dados desses limites são locais ao processo. CORS permite Authorization e expõe Retry-After e X-Request-ID.
Respostas têm X-Request-ID e Cache-Control: no-store. O cache interno do fornecedor continua funcionando.
Produção desabilita /docs, /redoc e /openapi.json; consulte a documentação em ambiente local.

## Prefixo na Vercel
Na URL publicada, acrescente /api às rotas deste documento: /api/health, /api/ready, /api/competitions, /api/matches e /api/matches/{id}/analysis. Localmente com backend.main, as rotas continuam sem prefixo. Os limites e métricas são por instância, inclusive na Vercel.
