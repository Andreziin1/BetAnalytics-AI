# Arquitetura atual
Backend em backend/main.py, com criação de aplicação injetável para testes.
Configuração em backend/config.py, integração em backend/api/football_api.py e funções puras em backend/analytics/team_analysis.py.
FastAPI expõe consultas GET; o cliente football-data.org concentra credenciais, timeout, erros, cache e quota.
A seleção estatística valida e filtra registros antes de calcular indicadores.
Uma falha no histórico de uma equipe ou no H2H preserva seções disponíveis e retorna avisos; falha na identificação da partida interrompe a consulta.
Frontend React/Vite em frontend: estrutura inicial e cliente REST preparado, sem análise visual integrada nesta fase.
Não há banco, scraping, ML ou dependência de Streamlit.
O .env é lido da raiz do projeto; variáveis de ambiente já definidas têm precedência.
A implantação pública e o compartilhamento de quotas entre workers são tarefas futuras.

