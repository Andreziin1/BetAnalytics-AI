# Entrega — BetAnalytics 1.4 — Vercel

## Correção de inicialização local — 23/10/2026
- O arquivo enviado foi lido com sucesso e a credencial foi aceita pela fonte. Não foi possível reproduzir aqui o estado exato do processo antigo no computador do usuário.
- Corrigido carregamento do `.env`: não contamina variáveis do processo, relê alterações e aceita UTF-8 com BOM. Na Vercel, ignora o arquivo local e usa apenas as variáveis do painel.
- Adicionados `iniciar.cmd` e `scripts/start_local.py` para iniciar os dois serviços juntos, confirmar a chave sem exibi-la e detectar portas ocupadas. Nesse iniciador local, o arquivo salvo prevalece sobre variáveis antigas do terminal.
- Restaurado o SVG do BPMN ausente nesta pasta enviada.
- A chave e os diretórios `.git`, `.venv` e `node_modules` não integram o ZIP corrigido. Preserve seu `.env` local ao aplicar os arquivos.
- Evidências desta revisão estão no início de `docs/validacao.md`; os resultados abaixo descrevem a entrega anterior.

## Alterações desta entrega
- Removidos Compose, Dockerfiles e Caddy.
- Criados app.py, vercel.json, .vercelignore, .python-version e comando de build para a Vercel.
- Frontend compilado em public/ para distribuição estática; backend FastAPI em /api no mesmo projeto.
- Produção obrigatória na Vercel, com chave da fonte e hashes dos códigos de acesso nas variáveis do servidor.
- Corrigida a identificação das rotas públicas sob /api e do IP encaminhado pela Vercel.
- Configurados cabeçalhos de segurança, API sem cache HTTP e duração máxima de 180 segundos.
- Atualizados README e guia docs/publicacao.md com importação, variáveis, Preview e verificação.

## Preservado
Seleção de liga, período, filtros, gráficos, histórico, H2H, acesso por código e cálculos descritivos. Nenhuma previsão ou dado esportivo inventado foi acrescentado. Fixtures sintéticas são usadas somente nos testes.

## Verificação
82 testes backend e um teste de integração frontend aprovados. Build de produção concluído. Configuração conferida contra o schema oficial da Vercel com Draft7Validator. Os detalhes e os resultados anteriores de consultas reais estão em docs/validacao.md.

## Para publicar
Siga docs/publicacao.md. Importe a raiz do projeto com preset FastAPI e configure API_KEY, APP_ENV=production e ACCESS_TOKEN_HASHES antes do primeiro deploy. O ZIP não contém credenciais. Se estiver substituindo uma pasta antiga, remova compose.yaml, .dockerignore e deploy/ manualmente.

A aplicação foi preparada, mas nenhum deploy na Vercel foi executado nesta entrega. O primeiro Preview deve ser validado com sua conta e suas variáveis. Cache, quotas preventivas e métricas permanecem em memória por instância; coordenação distribuída ainda é necessária para limites globais consistentes em escala. O BPMN da versão 1.3 continua representando o fluxo de análise preservado.
