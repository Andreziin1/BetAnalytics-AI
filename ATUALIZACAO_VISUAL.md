# BetAnalytics — atualização visual

## O que mudou

- Identidade visual verde escuro, painéis claros, tipografia local e ícone próprio.
- Navegação por campeonatos na lateral do desktop e seleção acessível no celular.
- Partidas em linhas compactas, agrupadas por dia de Brasília.
- Busca por equipe, filtro por data, atalhos de dia e ordenação.
- Análise em área própria, sem precisar percorrer toda a lista de jogos.
- Seções Visão geral, Últimos jogos, Confrontos diretos e Origem dos dados.
- Comparação de equipes, barras de resultados e médias de gols com valores textuais.
- Estados de carregamento, cancelamento, erros, ausência de jogos e amostra incompleta.
- Layout responsivo e detalhes de acessibilidade: foco, rótulos, contraste e movimento reduzido.
- Fontes locais licenciadas: a política de segurança da Vercel foi mantida.

O backend e os cálculos foram preservados. O frontend continua consumindo os mesmos endpoints. A aplicação apresenta estatísticas descritivas, não probabilidades calculadas por IA. Não foram adicionadas partidas, odds ou estatísticas simuladas à aplicação entregue.

## Atualizar no Windows

1. Faça uma cópia da pasta que está funcionando.
2. Extraia o ZIP em uma nova pasta.
3. Copie seu arquivo .env da raiz da versão anterior para a raiz da nova versão. Ele não foi incluído no pacote.
4. Abra a nova pasta no VS Code e execute no terminal PowerShell:

```powershell
.\iniciar.cmd
```

Para atualizar somente o frontend na instalação existente, copie a pasta frontend deste pacote, preservando qualquer configuração local necessária. Depois, em frontend, execute `npm ci` e `npm run dev`, mantendo o backend iniciado.

## Validações realizadas nesta atualização

- 86 testes Python aprovados, abrangendo backend, configuração, operações e integração Vercel.
- Fluxo automatizado de interface aprovado: busca, troca de liga, análise parcial, seções, retorno à lista, erro, vazio e cancelamento.
- Inspeção visual e interação no navegador: desktop e viewport mobile de 390 px em iframe de revisão; listas, análise e tabelas sem transbordamento horizontal da página.
- Build de produção e preparação de arquivos públicos pelo script da Vercel.

A revisão visual utilizou dados sintéticos em um ambiente separado. Esses dados e o servidor de revisão não fazem parte do ZIP. Não foi realizada uma nova consulta ao fornecedor esportivo com sua chave nesta atualização. A publicação real na Vercel não foi executada.

## Arquivos principais

- frontend/src/main.jsx — navegação, busca e calendário.
- frontend/src/Analysis.jsx — seções e comparação.
- frontend/src/UI.jsx — ícones e escudos com alternativa por iniciais.
- frontend/src/styles.css — identidade e responsividade.
- frontend/public — fontes e favicon.
- frontend/tests — testes ajustados ao novo fluxo.

A estrutura do backend e sua configuração de implantação foram preservadas.
