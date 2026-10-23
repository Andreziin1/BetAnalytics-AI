# Frontend React e Vite

Interface de futebol com seleção de campeonato/período, partidas futuras e análise visual integrada.

Requer Node 22.12+ ou 24. Na pasta frontend:
```sh
npm ci
npm run dev
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```
Mantenha o backend na porta 8000. `/api` é encaminhado pelo Vite ao backend, inclusive quando a porta local muda. `npm run preview` também possui proxy local. Na hospedagem estática, configure um proxy ou VITE_API_BASE_URL e CORS no servidor.
Nunca coloque API_KEY em variáveis VITE_: elas são públicas.

## Análise
Clique em Ver análise. A seção abaixo da lista apresenta comparação, gols, médias, forma recente, históricos expansíveis, H2H e qualidade dos dados. Valores null aparecem como Indisponível; zero continua sendo zero. W/D/L é traduzido para V/E/D, do mais recente ao mais antigo. Datas usam Brasília; a janela de busca é definida em datas UTC.

Consultas anteriores são canceladas ao trocar a análise ou iniciar nova busca. O cancelamento interrompe a espera do navegador, mas não garante interromper uma chamada que o backend já enviou ao fornecedor.

## Testes
`npm test` executa o fluxo em jsdom, com respostas sintéticas explicitamente identificadas em tests/analysis.fixture.json. Cobre busca, análise parcial, histórico, vazio, HTTP 429 e cancelamento. Não substitui teste visual ou acesso ao fornecedor real.

## Funcionalidades 1.3
Filtros por nome sem acentos e data local, ordenação por proximidade, gráficos V/E/D e médias de gols, detalhamento casa/fora e retorno à lista. Escudos HTTPS inválidos usam iniciais como fallback. Gráficos possuem números textuais; null nunca vira zero.

Acesso por código: quando o backend responde 401, a tela solicita código individual. Ele é enviado em Authorization e mantido somente em memória. API_KEY nunca deve ser digitada nessa tela. Ao recarregar, o código é descartado.

O teste E2E inicia Vite na porta 5179 automaticamente; usa fixtures e Chromium em 1440 e 390 pixels. Não depende de backend ou chave real. PLAYWRIGHT_EXECUTABLE_PATH permite um Chromium já instalado; E2E_BASE_URL permite frontend iniciado. Capturas são opcionais via E2E_SCREENSHOT_DIR e destinadas a QA local.

## Vercel
O projeto é publicado a partir da raiz com preset FastAPI, não diretamente desta pasta. O script de build gera public/ para a CDN; a API é acessada em /api no mesmo domínio. Não é necessário VITE_API_BASE_URL e nunca se deve usar localhost em produção. A configuração do proxy em vite.config.js é somente para desenvolvimento/preview local.
