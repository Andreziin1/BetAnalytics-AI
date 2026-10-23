# Escopo vigente — BetAnalytics 1.4

Exclusivamente futebol e análise descritiva. Não utiliza IA/ML, odds ou previsões.

## Implementado e validado
- Backend FastAPI e frontend React/Vite integrados.
- Até dez jogos válidos por equipe e cinco confrontos diretos, com amostras reais e avisos.
- Filtros por campeonato, time, data e ordenação; gráficos V/E/D e gols; desempenho casa/fora; históricos.
- Carregamento, vazio, erro, cancelamento, fallback de escudos e navegação com foco.
- Acesso por código individual quando configurado; obrigatório em produção.
- Quotas por usuário/IP, cache e limite preventivo do fornecedor por instância; cooldown em 429.
- Logs estruturados sem segredos, /health, /ready, /metrics e sonda para monitor externo.
- BPMN em imagem, vetor e XML editável.
- Testes automatizados, inspeção em Chromium desktop/celular e validação real da fonte.

## Preparado, dependente de ambiente
Vercel/FastAPI, arquivos estáticos na CDN, HTTPS da plataforma e guia de configuração. Requer importar o repositório e cadastrar variáveis; não foi publicado nesta tarefa.

## Limites assumidos
Dados, quotas e métricas em memória por instância. Na Vercel há escala automática; para garantir limites globais, implementar cache/quota distribuídos. Códigos são provisionados pelo administrador; não há cadastro público/recuperação de senha. Monitor externo/alertas dependem do serviço do proprietário.

A amostra H2H pode ter menos de cinco jogos. Nada é preenchido artificialmente. Datas de corte não são snapshots históricos para backtesting.
