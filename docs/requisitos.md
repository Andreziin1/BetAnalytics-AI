# Escopo do Projeto — BetAnalytics

> Versão atual: backend e frontend integrados. Consulte escopo_atual.md e api.md. Escopo exclusivamente de futebol e análise descritiva.

## 1. Nome do projeto

BetAnalytics

## 2. Descrição

O BetAnalytics é uma plataforma de análise estatística pré-jogo de futebol baseada em dados históricos de partidas.

O sistema tem como objetivo reunir informações recentes das equipes, calcular estatísticas básicas de desempenho e apresentar os dados de forma organizada para auxiliar na análise de uma partida.

A primeira versão do projeto possui foco em análise descritiva, sem realizar previsões ou recomendações de apostas.

## 3. Objetivo principal

Criar um sistema em Python capaz de:

- coletar dados esportivos;
- consultar partidas futuras;
- analisar os últimos jogos das equipes;
- calcular estatísticas de desempenho;
- apresentar a forma recente das equipes;
- consultar confrontos diretos;
- apresentar os últimos confrontos entre as equipes;
- disponibilizar os dados através de uma API;
- apresentar as informações em uma interface simples para o usuário.

## 4. Esportes previstos

### V1

- Futebol

## 5. Funcionalidades da V1

- Consultar partidas futuras
- Selecionar uma partida
- Identificar os times mandante e visitante
- Consultar os últimos 10 jogos de cada time
- Exibir vitórias, empates e derrotas
- Exibir gols marcados e sofridos
- Calcular média de gols marcados
- Calcular média de gols sofridos
- Exibir a forma recente dos times
- Exibir os últimos jogos de cada equipe
- Consultar confrontos diretos
- Exibir até 5 confrontos diretos disponíveis
- Apresentar uma análise consolidada da partida
- Disponibilizar os dados através de uma API REST
- Interface para visualização dos dados

## 6. Fluxo principal do sistema

1. Usuário escolhe campeonato e período e solicita os jogos.
2. Backend consulta a fonte e devolve partidas disponíveis ou avisos/erros.
3. Usuário seleciona uma partida.
4. Backend identifica as equipes, obtém e valida históricos e confrontos.
5. Calcula indicadores apenas sobre os jogos válidos disponíveis.
6. Frontend apresenta análise, tamanho da amostra, históricos e limitações.

Ver `fluxo_atual.md` para decisões de erro e disponibilidade parcial.

## Requisitos adicionais implementados na 1.3
Filtros por time/data, gráficos descritivos, ordenação, responsividade, navegação acessível, fallback de escudos, acesso por código, limites, logs e preparação de implantação. Ver escopo_atual.md para limites e publicacao.md para operação.
