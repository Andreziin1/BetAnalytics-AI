# Frontend React e Vite
Esta fase inclui a seleção de campeonato e período, seguida da listagem de partidas reais.
O botão de cada jogo abre o JSON de análise daquela partida; a apresentação visual completa ainda será implementada.

Requer Node 22.12+ (ou Node 24). Na pasta frontend:
```sh
npm ci
npm run dev
npm run build
```
Abra no Chrome o endereço mostrado pelo Vite. Mantenha o backend ativo na porta 8000.
O endereço padrão da API é `/api`, encaminhado pelo Vite ao backend. Assim a troca automática de porta do frontend não gera bloqueio de CORS.
Se você já possui frontend/.env com VITE_API_BASE_URL, use `VITE_API_BASE_URL=/api` e reinicie o Vite.
VITE_API_BASE_URL é público; nunca colocar a chave esportiva no frontend.
O build estático exige configurar esse encaminhamento na hospedagem, ou definir uma API externa com CORS. Esta entrega permanece local.

## Próxima fase
- Análise lado a lado, denominadores, V/E/D e médias.
- Históricos e H2H, identificado pela propriedade head_to_head.matches.
- Estados de carregamento, vazio, falha, resultado parcial e cancelamento de requisições.
- Mostrar warnings, origem, corte temporal e retrieved_at.
- Tratar null como indisponível; zero é um valor real.
- Traduzir W/D/L para V/E/D; ordem do mais recente ao mais antigo.
- Acessibilidade, responsividade e testes de integração visual.

