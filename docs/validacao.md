# Validação da atualização visual

Nesta atualização: 86 testes Python aprovados; fluxo de interface DOM aprovado; build de produção/Vercel aprovado; revisão visual em desktop e viewport mobile de 390 px. Foram usados dados sintéticos em ambiente separado para revisão da interface, sem nova consulta ao fornecedor com a chave do usuário. Não houve deploy real. Detalhes em ../ATUALIZACAO_VISUAL.md.

---

## Registros das versões anteriores

# Validação — BetAnalytics 1.4 — 23/10/2026

## Revisão da pasta reenviada — inicialização local
- Antes da correção: chave do arquivo reconhecida; 81 testes passaram e um falhou porque a simulação Vercel carregava APP_ENV do arquivo local. O erro da máquina do usuário (chave ausente em processo já iniciado) não foi reproduzido com este ZIP.
- Após a correção: 86 testes backend aprovados, incluindo leitura UTF-8 com BOM, releitura do arquivo, precedência de variáveis e isolamento da configuração Vercel.
- Um teste de integração DOM e três testes em Chromium aprovados: desktop 1440 px, celular 390 px e autenticação. O teste de cancelamento agora controla a liberação da resposta simulada, sem depender de uma corrida de 300 ms.
- Iniciador único testado neste ambiente Linux: abriu frontend/backend, confirmou /health e encerrou ambos. Também reconheceu a chave do arquivo mesmo recebendo uma variável API_KEY antiga de exemplo. O wrapper iniciar.cmd não foi executado em Windows neste ambiente.
- Fluxo real em Chromium, sem respostas simuladas: seleção BSA, 17 partidas, abertura da análise da partida 555052, gráfico visível, HTTP 200 na listagem e análise, nenhum erro JavaScript. A integração usou Vite /api e FastAPI juntos.
- Consulta real registrada em 23/10/2026, às 13:32:36 de Brasília: dez jogos válidos por equipe e um confronto direto; amostra H2H incompleta sinalizada. A chave foi utilizada pelo backend e não integra este relatório nem o pacote final.
- Build completo para Vercel aprovado. npm audit --omit=dev: zero vulnerabilidades reportadas nas dependências de produção naquele momento.
- A implantação hospedada na Vercel ainda não foi executada. Os resultados de dados variam com a disponibilidade e os limites da fonte; não garantem que todas as partidas tenham histórico completo.

As seções seguintes registram a entrega anterior.

## Adaptação para Vercel (1.4)
- 82 testes backend aprovados, incluindo prefixo /api, autenticação, health público e IP encaminhado somente no ambiente Vercel.
- Um teste de integração frontend aprovado novamente.
- Build completo scripts/build_vercel.py concluído, gerando public/index.html e assets.
- vercel.json validado com Draft7Validator contra o schema oficial. O schema publicado mistura construções de diferentes drafts; sua autovalidação genérica falha em experimentalTriggers, campo não utilizado pelo projeto.
- Nenhum deploy Vercel foi realizado; é necessário validar um Preview na conta de destino.

## Evidências da versão anterior (1.3)
Os resultados abaixo foram obtidos antes da adaptação de hospedagem; não representam um teste online na Vercel.

## Testes de software
- Backend: 74 testes aprovados, incluindo acesso, limites por usuário/IP, CORS e ausência de segredos nos logs.
- Frontend DOM simulado: um teste de integração com múltiplas verificações aprovado.
- Chromium real 153: três testes aprovados (fluxos desktop 1440 px, celular 390 px e acesso por código).
- Inspeção visual das capturas desktop/celular realizada; sem transbordamento horizontal da página. Tabelas extensas possuem rolagem própria.
- Build Vite 7.3.7 concluído.
- npm audit após dependências finais: zero vulnerabilidades conhecidas reportadas.
- Auditoria Python realizada na revisão anterior, sem alteração dos requirements nesta versão: nenhuma vulnerabilidade conhecida então reportada. Não equivale a garantia de segurança.
- BPMN em SVG/PNG inspecionado; XML verificado com parser BPMN.

## Integração real com football-data.org
Foi usada a credencial já presente no ZIP original, somente em memória. Nenhuma chave integra a entrega.

Busca Premier League: HTTP 200, 10 partidas futuras no momento da consulta.
Análise da partida 560620: HTTP 200, 10 jogos válidos do mandante, 10 do visitante e 2 H2H. O aviso insufficient_history sinalizou corretamente a amostra H2H abaixo de cinco.

Consulta das nove competições em 2026-10-23T14:39:27.485287+00:00: PL, PD, SA, BL1, FL1, CL, PPL, BSA, DED, sem falhas por competição e 93 partidas no total para sete datas UTC. A existência de acesso não garante quantidade histórica, temporada inteira ou disponibilidade futura. Não foram testadas análises de todas as partidas/ligas.

## Testes do navegador
As respostas nos testes do navegador são fixtures sintéticas explicitamente identificadas, independentes da validação externa acima. Cobrem filtros de time sem acento, data de Brasília, ordenação, vazio, gráficos, históricos, retorno do foco, erro 429, cancelamento sem resposta tardia e código de acesso sem armazenamento persistente.

## Limitações restantes
- Docker/Caddy foram removidos na versão 1.4. A configuração Vercel ainda precisa de teste no ambiente hospedado.
- Nenhum domínio, hospedagem, certificado público ou serviço externo de alertas foi provisionado.
- Responsividade inspecionada em Chromium, não em dispositivos físicos ou todos os navegadores; auditoria completa por leitor de tela e carga não realizada.
- Um aviso de depreciação Starlette/httpx permanece na suíte, sem falhas.
- Cache, limites preventivos e métricas são locais à instância. A Vercel pode criar várias instâncias; não há coordenação distribuída de quotas nesta versão.
