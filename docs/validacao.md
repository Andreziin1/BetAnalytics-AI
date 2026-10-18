# Registro de validação

Revisão de 17 de outubro de 2026, a partir do ZIP recebido.

- 53 testes automatizados aprovados em Python 3.12. A suíte usa fixtures e mocks; não substitui a integração real.
- Build do frontend React/Vite aprovado com `npm run build`.
- Integração HTTP real pelo proxy do Vite na porta 5174: `/api/health` retornou 200; a busca da Premier League para sete dias retornou 200 e seis partidas futuras.
- Análise real da partida 560604 pelo mesmo proxy: HTTP 200, dez jogos por equipe e dois confrontos diretos. O aviso `insufficient_history` indicou corretamente que o H2H não completou cinco jogos.
- O `.env` recebido continha um texto de exemplo como chave. O fornecedor respondeu HTTP 400 com indicação de token inválido. Agora o backend reconhece esse erro como autenticação e ignora marcadores comuns de chave de exemplo.
- Os testes também verificam o corte do histórico por horário, incluindo jogos anteriores no mesmo dia, e o reconhecimento de LEAGUE_CUP como competição oficial.
- A suíte emitiu um aviso de depreciação Starlette TestClient/httpx, sem falhas.

O teste de integração usou uma credencial configurada separadamente. Nenhuma credencial acompanha este pacote. Configure sua própria API_KEY no `.env` da raiz.

Limitações: não foram testadas todas as ligas, assinaturas, carga ou implantação pública. Não foi concluída a validação visual em navegador: o ambiente não disponibilizou Chromium funcional. O build e a comunicação HTTP foram verificados, mas não equivalem a um teste visual ponta a ponta. A tela é um escopo inicial React, com seleção de campeonato, lista de jogos e link para análise em JSON.

Uma consulta bem-sucedida não garante disponibilidade futura da API. A quantidade de jogos muda conforme o horário da consulta. Leia README.md para executar localmente.
