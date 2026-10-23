# Arquitetura atual
Backend em backend/main.py, com criação de aplicação injetável para testes.
Configuração em backend/config.py, integração em backend/api/football_api.py e funções puras em backend/analytics/team_analysis.py.
FastAPI expõe consultas GET; o cliente football-data.org concentra credenciais, timeout, erros, cache e quota.
A seleção estatística valida e filtra registros antes de calcular indicadores.
Uma falha no histórico de uma equipe ou no H2H preserva seções disponíveis e retorna avisos; falha na identificação da partida interrompe a consulta.
Frontend React/Vite em frontend: listagem em src/main.jsx e análise visual em src/Analysis.jsx, com cliente REST em src/api.js.
Não há banco, scraping, ML ou dependência de Streamlit.
O .env é lido da raiz do projeto; variáveis de ambiente já definidas têm precedência.
A implantação está preparada em app.py, vercel.json e scripts/build_vercel.py. A Vercel pode criar várias instâncias: os limites em memória não constituem quota distribuída.


Requisições de análise anteriores são canceladas ao selecionar outra partida, buscar novamente ou desmontar a tela. Cache e Session são protegidos por lock; consultas externas são serializadas nesta versão local.

backend/operations.py implementa autenticação por hash de códigos, limite por usuário/IP e métricas locais. Middleware CORS envolve as respostas de autenticação. Logs não incluem cabeçalhos, query strings ou corpos.
frontend/src/Charts.jsx contém gráficos CSS com valores textuais acessíveis; nenhum dado é inventado. Filtros operam sobre partidas já consultadas e não consomem a quota.
A Vercel serve public/ pela CDN e executa app.py como função FastAPI. O backend é montado em /api; o código original de análise foi preservado. HTTPS é gerenciado pela plataforma.
