# Contrato REST versão 1.1

Documentação de parâmetros em /docs e /openapi.json.
Datas retornadas em ISO 8601 com fuso UTC. Valores monetários e odds não fazem parte desta API.

## Listagem
GET /matches?days=7&competitions=PL,BSA
days aceita 1 a 30; representa datas UTC incluindo hoje, excluindo partidas cujo horário já passou.
competitions é opcional, separado por vírgulas. Lista permitida em /competitions; acesso efetivo depende da assinatura.
Resposta: matches (lista), discarded (quantidade de registros inválidos), days e timezone.
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
warnings contém objetos code, section, message.
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
O frontend antigo deve ser adaptado antes de ser reutilizado.

