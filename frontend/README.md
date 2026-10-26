# Frontend React e Vite

Interface de análise de futebol: campeonatos, partidas futuras, filtros locais e uma área dedicada para cada análise.

## Executar

Use Node 22.12+ ou 24. Na pasta frontend:

```sh
npm ci
npm run dev
```

Mantenha o backend na porta 8000. O proxy do Vite encaminha `/api` ao backend. Na raiz do projeto, `iniciar.cmd` continua sendo o ponto de entrada no Windows.

Nunca coloque API_KEY em variáveis VITE_: elas são públicas.

## Navegação

- Desktop: barra lateral com campeonatos. Clicar numa liga busca os jogos usando o período selecionado.
- Todas as telas: seletor de campeonato e período com botão Buscar jogos.
- Lista agrupada por data de Brasília, busca por time sem distinção de acentos, filtro de dia e ordenação.
- Ver análise abre uma área dedicada; a lista e seus filtros são preservados ao voltar.
- Visão geral: resultados, forma recente, médias de gols e recortes casa/fora.
- Últimos jogos: histórico de cada equipe.
- Confrontos diretos: até cinco encontros válidos, com resumo e tabela.
- Origem dos dados: fonte, horários de coleta e limitações.
- Avisos de amostra parcial sempre identificados, com detalhes expansíveis.

Valores ausentes aparecem como Indisponível, não como zero. V/E/D corresponde a vitória/empate/derrota; a forma começa pelo jogo mais recente. A busca usa datas UTC; a apresentação e os filtros locais usam Brasília.

Escudos HTTPS que falham usam iniciais. Ícones são SVG locais. As fontes DM Sans e Manrope são locais, com licenças em public/fonts. Não há dependência de Google Fonts em produção. Layout responsivo, foco visível, atalho para o conteúdo e suporte a movimento reduzido.

Consultas anteriores são canceladas ao iniciar outra busca ou fechar a análise. O cancelamento interrompe a espera no navegador, mas não garante interromper uma chamada já enviada pelo backend ao fornecedor.

Acesso por código: uma resposta 401 solicita o código individual. Ele é enviado em Authorization e fica apenas em memória. A API_KEY esportiva deve permanecer no .env do backend.

## Validação

```sh
npm test
npm run build
```

O teste de interface usa jsdom e dados sintéticos: busca, troca de campeonato, área dedicada, seções de análise, retorno de foco, dados parciais, vazio, HTTP 429 e cancelamento.

Para executar a suíte de navegador localmente:

```sh
npx playwright install chromium
npm run test:e2e
```

Ela inicia Vite na porta 5179 e utiliza respostas sintéticas em 1440 e 390 pixels. PLAYWRIGHT_EXECUTABLE_PATH aceita um Chromium instalado; E2E_BASE_URL aceita um frontend já iniciado. Capturas opcionais via E2E_SCREENSHOT_DIR são destinadas à revisão local.

## Vercel

Publique pela raiz com o preset FastAPI. `python scripts/build_vercel.py` instala o frontend, gera o build e prepara public/. A API permanece em /api no mesmo domínio. Nenhuma alteração nas rotas do backend foi necessária para o novo visual. Não configure localhost em produção.
