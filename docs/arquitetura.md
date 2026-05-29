# arquitetura.md

# Arquitetura do Projeto — BetAnalytics IA

## Objetivo da arquitetura

A arquitetura do BetAnalytics IA foi planejada para permitir organização, escalabilidade e separação de responsabilidades entre os módulos do sistema.

O projeto utiliza uma estrutura modular para facilitar manutenção, expansão futura e integração de novos esportes e funcionalidades.

---

# Fluxo geral do sistema

```text
Usuário
   ↓
Interface Streamlit
   ↓
Requisição de dados
   ↓
APIs / Scraping
   ↓
Tratamento de dados (ETL)
   ↓
Análise estatística
   ↓
Cálculo de probabilidades
   ↓
Sugestões estatísticas
   ↓
Dashboard e relatórios