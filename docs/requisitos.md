# Escopo do Projeto — BetAnalytics IA

> Atualização desta fase: frontend obrigatório em React + Vite, entregue apenas como estrutura inicial. Backend revisado nesta entrega. Consulte escopo_atual.md e api.md para regras e contrato vigentes; probabilidades e outros esportes permanecem fora da V1.

## 1. Nome do projeto

BetAnalytics IA

## 2. Descrição

O BetAnalytics IA é uma plataforma de análise estatística pré-jogo de futebol baseada em dados históricos de partidas.

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

### Futuras versões

- NBA
- NFL
- UFC
- Fórmula 1
- Tênis
- NHL
- Boxe
- Vôlei

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

```text
Usuário acessa o BetAnalytics IA
                ↓
Sistema consulta partidas futuras
                ↓
Usuário seleciona uma partida
                ↓
Sistema identifica os dois times
                ↓
Busca os últimos 10 jogos de cada time
                ↓
Calcula as estatísticas
                ↓
Busca os confrontos diretos
                ↓
Organiza os últimos 5 confrontos
                ↓
API retorna a análise
                ↓
Frontend apresenta os dados
                ↓
Usuário visualiza a análise
