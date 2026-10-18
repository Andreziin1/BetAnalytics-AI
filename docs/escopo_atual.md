# Escopo vigente após manutenção

Este documento atualiza os requisitos anteriores e prevalece sobre referências a Streamlit, multiesportes ou interface opcional.
A V1 final terá backend FastAPI e frontend React com Vite. Nesta entrega a implementação completa de telas permanece para a fase seguinte.

## Entregue nesta fase
- Revisão do backend: configuração, imports a partir da raiz, integração, erros seguros, cache e quota local.
- Regras de seleção e cálculo, datas, duplicatas, nulos, placares e validação de H2H.
- Resumos de equipe, percentuais descritivos, subgrupos casa/fora e agregados H2H.
- Avisos por seção e rastreabilidade da origem, horário de coleta e corte.
- Testes reproduzíveis sem API real.
- Interface React/Vite para selecionar campeonato e período e listar partidas reais.
- Documentação de instalação e contrato atualizado.

## Próxima fase do frontend
Apresentação da análise, comparação, históricos e avisos de qualidade dos dados.
O frontend é obrigatório para concluir a V1, mas não está funcionalmente integrado nesta entrega.

## Fora desta fase
Previsões probabilísticas, recomendações, ML, outros esportes e deploy público.
A frequência histórica de vitórias não é uma previsão de vitória futura.

## Critérios
Testes devem cobrir placares ausentes/inválidos, orientação mandante/visitante, ordenação,
corte temporal, duplicatas, dados incompletos, H2H e respostas HTTP.
Disponibilidade e autorização reais do fornecedor exigem validação com a assinatura utilizada.

