# backlog · opencode prefs v2

legenda: `[feito]`, `[parcial]`, `[aberto]`, `[bloqueado]`, `[descartado]`.

## concluído

- [feito] criada instalação local isolada do OpenCode `1.18.30`, sem alterar
  `PATH` ou estado global; evidência: `docs/OPENCODE-ISOLATED.md`.
- [feito] criada a fundação documental: `docs/core/` e `docs/additive/`.
- [feito] consolidado o contexto recuperável da conversa anterior; fonte:
  `docs/additive/CONTEXT-2026-09-10.md`.
- [feito] 2026-09-10: ampliado `AGENTS.md` com contratos documentais e limites
  operacionais; criado `CLAUDE.md -> AGENTS.md` relativo. validação:
  `test -L CLAUDE.md`, `readlink CLAUDE.md` retornou `AGENTS.md` e
  `cmp AGENTS.md CLAUDE.md` passou. decisão: D-004.
- [feito] 2026-09-11: estrutura piloto do vault obsidian criada em `vault/`
  com índice e pastas; proposta atualizada em
  `docs/additive/VAULT-2026-09-11.md`. nenhuma decisão registrada ainda.

## aberto

- [feito, configuração; acesso funcional pendente] usuário autorizou patch
  temporário de `external_directory` somente no `explorer-gpt`, restrito aos seis
  projetos da varredura. `./scripts/rtk-local.sh run ./opencode-isolated debug agent
  explorer-gpt` concluiu com exit 0 e mostrou os seis allows, deny externo geral,
  `bash: false`, `apply_patch: false` e bloqueios read de `.env*`/`auth.json`.
  Não prova leitura externa efetiva nem sandbox. Requer reinício e smoke de leitura.
  Diagnóstico também retornou `variant: low`; override medium anteriormente salvo
  não ficou comprovado nesse comando. Conferir aplicação antes da leitura extensa.
- [feito] 2026-09-16: bloco temporário `external_directory` removido de
  `v2/agent/explorer-gpt.md` após concluir a varredura (D-039). `debug agent`
  confirma apenas `external_directory: ask` e os caminhos internos de tool-output;
  os seis allows sumiram e bash/apply_patch continuam negados. Reconceder exige
  novo patch explícito e restart. O mesmo diagnóstico mostrou `variant: low`,
  reforçando que `debug agent` reflete o frontmatter, não o override do plugin.
- [feito] 2026-09-16: varredura comparativa concluída com acesso autorizado.
  Sete projetos examinados; comparação em
  `vault/agents/projetos/HARNESS-COMPARATIVO-2026-09-16.md` e cobertura em
  `HARNESS-CORPUS` (vault); catálogo ampliado para H01–H28 em
  `HARNESS-PROPOSTA` (vault). Relatórios R1 marcados como históricos.
  Nenhuma proposta implementada, nenhum projeto externo alterado, nenhum produto
  executado. Pendências declaradas: Git remoto sem autenticação, effort efetivo
  não capturado, primeira linha do plugin agora lida como `contrein`, e leitura
  não cobre specs de domínio, planilhas e corpus público.
- [feito, pendente prova em sessão] 2026-09-16: anomalia do plugin confirmada e
  corrigida. Evidência decisiva: após o restart desta rodada, a sessão deixou de
  anunciar `subconfig`, `sessions_*` e `team_spawn`, ou seja, o módulo não
  carregou; isso também explica o override salvo nunca aplicado. Removido o
  token solto `contrein` da primeira linha de `v2/plugins/session-bridge.mjs`;
  `node --check` passou e `import()` retornou `function`. Import isolado não
  prova registro das tools no runtime: confirmar no próximo boot.
  Confirmado após reinício: `subconfig reload` respondeu com índice de 6 agentes
  lógicos e 38 modelos, ou seja, o plugin voltou a carregar e registrar tools.
- [feito, aguarda restart] 2026-09-16: usuário informou limite da assinatura GPT
  e pediu explorer em Sonnet. Como `subconfig` estava indisponível na sessão, o
  override foi escrito diretamente em `v2/subagent-models.json` no mesmo formato
  da tool: `explorer` → `anthropic/claude-sonnet-4-6`, `medium` (catálogo local
  confirma low/medium/high/max nesse modelo). Simulação de `applyOverrides`
  resolve `explorer-gpt` e `explorer-claude` para Sonnet. Frontmatters de
  `v2/agent/*.md` não foram alterados. `summarizer-gpt` continua apontando para
  Luna e deve falhar enquanto durar o limite; decisão do usuário.
  Confirmado após reinício: `debug agent` mostra `explorer-gpt` e
  `explorer-claude` em `anthropic/claude-sonnet-4-6`/`medium` — o hook do plugin
  passou a valer também nesse diagnóstico. Smoke real de delegação leu
  `docs/INDEX.md`, contou os cinco relatórios HARNESS e reportou negativa
  correta ao tentar o `AGENTS.md` de um projeto externo, sem tentar contornar.
  Isso prova modelo aplicado, retorno de subagente e revogação da exceção D-039.
- [feito, aguarda restart] 2026-09-16: catálogo unificado (D-040). Criados
  `coder-basic`, `coder-plus`, `coder-pro`, `explorer`, `summarizer` e
  `reviewer` a partir dos antigos arquivos `-gpt`, com modelos Anthropic por
  causa do limite GPT: Haiku high (basic/summarizer), Sonnet 4.6 medium
  (plus/explorer) e Opus 5 high (pro/reviewer). Removidos os 12 pareados após
  `diff` confirmar corpo e permissões idênticos fora de modelo/variant.
  `AGENT_TARGETS` passou a mapear cada papel para um alvo; overrides migrados em
  `v2/subagent-models.json` (`summarizer-gpt` saiu, `coder-plus` e `explorer`
  preservados). Evidências: `check-v2.py` com **10 agentes e 0 falhas**, roster
  e ausência de sufixos verificados; 38 testes Python OK; 10 testes Node OK após
  atualizar fixtures que ainda usavam nomes pareados. `subconfig reload` nesta
  sessão ainda devolve os pares antigos porque o plugin foi carregado no boot
  anterior — reconferir após reiniciar.
  Confirmado após reinício: `subconfig reload` lista os seis papéis com um alvo
  cada; `debug agent` resolve `coder-basic` Haiku high, `coder-plus`
  `opencode/muse-spark-1.3-contributor-free` medium (override do usuário
  preservado, sobrepondo o padrão Sonnet), `coder-pro` Opus 5 high, `explorer`
  Sonnet 4.6 medium, `summarizer` Haiku high e `reviewer` Opus 5 high. Fronteiras
  mantidas: `task` negado nos seis; `bash` só nos três coders. Smoke de delegação
  com o novo `explorer` listou os 10 arquivos de `v2/agent/` e confirmou ausência
  de sufixos de provedor.
- [aberto] investigar confiabilidade do harness observada na varredura:
  retomadas de `task_id` que devolvem relatório antigo, resumos de leitura com
  faixas impossíveis, PDF sem texto para delegado mas com texto para o principal,
  RTK `run` perdendo quoting de caminho com espaços e MarkItDown sem extras PDF.
  Fatos observados; causas não isoladas e sem correção nesta rodada.

- [parcial] 2026-09-16: diagnóstico do harness contra processo histórico e V2
  documentado em `vault/agents/projetos/HARNESS-DIAGNOSTICO-2026-09-16.md`, com cobertura
  em `HARNESS-EVIDENCIAS` (vault) e propostas categorizadas em
  `HARNESS-PROPOSTA` (vault). Leitura bruta delegada a explorer-gpt;
  evidências centrais conferidas pelo responsável. Nenhuma proposta implementada.
  Revisão independente documental encontrou dois achados médios e um baixo
  (dependência universal indevida, mistura histórico/ativo e referências móveis);
  corrigidos e reconferidos pelo mesmo revisor, sem pendências nesses achados.
- [bloqueado] completar varredura comparativa: leitura dos seis projetos externos
  negada aos subagentes (os seis projetos externos autorizados). Autorização humana de pesquisa foi dada,
  mas não resolveu acesso efetivo; não houve bypass. Resolver permissão read-only
  por mecanismo autorizado, provar acesso antes de novo fan-out e retomar os IDs
  registrados no relatório. Fontes secundárias não substituem as primárias.
- [aberto] retomar o pedido original após compactação: debate das propostas com
  o usuário, começando por evidência de conclusão, dono da integração e
  continuidade de estado. Pacote de continuidade em
  `vault/agents/projetos/HARNESS-HANDOFF-2026-09-16.md`; entrada técnica em
  `HARNESS-COMPARATIVO` (vault). Implementação continua não autorizada.
- [aberto] debater propostas H01–H18 distinguindo achados locais já sustentados
  de hipóteses dependentes das fontes externas. A comparação personalizada segue
  bloqueada; o debate local pode avançar sem autorizar implementação. Prioridades
  no relatório são recomendações, não aprovação nem fila concorrente.
- [resolvido em 2026-09-16] a anomalia `cont` em `v2/plugins/session-bridge.mjs:1`
  não existe mais: a linha 1 é `import { tool } from "@opencode-ai/plugin";` e o
  plugin carrega, com as tools registradas e 11 testes Node passando. o token
  solto foi corrigido na rodada do catálogo unificado; esta entrada ficou
  desatualizada. registro original abaixo.
- [histórico] investigar anomalia `cont` em `v2/plugins/session-bridge.mjs:1`,
  confirmada por leitura direta nesta rodada. Possível falha de avaliação no
  próximo carregamento; sem reprodução de boot/import e sem correção no escopo
  de diagnóstico. Smoke histórico não valida automaticamente o arquivo atual.

- [aberto] completar leitura do corpus `prompt-reference/` no SHA
  `f475e8b2b11ca7540a37234a451e9f085471bd94`: relatório consolidado confirma
  no mínimo 192/433 textos com EOF; restante não comprovado. lote posterior
  Claude Code confirmou 6 arquivos, ainda sem deduplicação com o consolidado.
  detalhes em `docs/additive/PROMPT-READINGS.md`. não declarar leitura total.
- [feito] revisar e enxugar `docs/additive/PROMPT-PROPOSAL.md`, confrontar
  composição com código oficial 1.18.30 e validar a configuração sem substituir
  o binário/prompt nativo; evidências em `INTEGRATION-1.18.30.md` e nos testes
  de sessão registrados abaixo.
- [bloqueado] leitura dos prompts Unigma pelo teammate: acesso externo negado;
  pesquisa do corpus público não substitui essa fonte local.

- [aberto] validar inventário/versões e viabilidade das políticas aprovadas em
  D-006–D-010 (composição, exposição provisória, rede, persistência e telemetria).
  executar aceitação por componente antes de ativar; pesquisa inicial:
  `docs/additive/CAPABILITIES-2026-09-10.md`.

- [feito] consolidado contrato mínimo em `docs/core/CONTRACT.md`, a partir das
  respostas aprovadas; D-024 confirma quatro principais na v1 e inferência de
  detalhes técnicos. não comprova implementação nem encerra permissões pendentes.
- [aberto] fechar pendências do contrato (catálogo/permissões/modelos, equipes)
  e executar provas de aceitação antes de declarar a base pronta.
- [feito] alinhada a localização de `LOGIC.md` à fundação `docs/core/` e
  atualizados índice, README e referências.
- [feito] auditar a base isolada: versão, instruções, ferramentas e origens;
  evidência em `docs/additive/AUDIT-ISOLATED-2026-09-12.md` e validações de
  sessão abaixo.
- [aberto] inventariar o legado e classificar cada item como necessário,
  quebrado, abandonado ou incerto. nenhum item incerto entra por padrão.
- [aberto] validar documentação de projeto como memória da base (D-015);
  memória global automática adiada, não implementar nesta fase.
- [aberto] validar piloto do vault obsidian (leitura, escrita automática,
  índice, links, deduplicação); proposta em
  `docs/additive/VAULT-2026-09-11.md`.
- [aberto] investigar exposição dinâmica de MCPs; conjuntos fixos são a escolha
  provisória, não prova de impossibilidade do carregamento sob demanda.
- [feito] verificar composição/ordem efetiva, kernel e carregamento nativo de
  `AGENTS.md`; bug do flag corrigido e marcadores confirmados em sessão real.
- [aberto] fechar catálogo assimétrico de subagentes, tiers/modelos GPT/Claude,
  permissões, MCPs e ownership; confirmar exclusividade de equipes ao Leader.
- [aberto] validar coordenação central de verificações, limites globais, regras
  por projeto, alternância de família e política Git desejada sem violar runtime.
- [feito] pesquisa documental V2-SESSIONS-RESEARCH retomada no effort disponível
  após autorização; bloqueio medium superado sem elevação. evidências e correção
  da hipótese Ensemble em `docs/additive/SESSIONS-2026-09-11.md`.
- [parcial] resolver integração de sessões independentes no Zed (D-021): o
  bridge local comprova sessões V2 no mesmo projeto, mas não federação global,
  FIFO, cross-project ou navegação completa de filhos.
- [feito] experimento local de sessões independentes compatível com
  `1.18.30`/ACP/Zed executado; pendem apenas os cenários fora do bridge local e
  a confirmação ponta a ponta do wake automático.
- [aberto] selecionar incrementalmente componentes aceitos no repositório V2 e
  validar cada inclusão antes da próxima.

## bloqueios e dependências

- [feito] configuração base V2 ativa e auditada; componentes futuros continuam
  sujeitos a prova incremental e não entram por herança implícita.
- [bloqueado] migração de qualquer componente legado: depende do inventário e
  da prova de finalidade e funcionamento.

## etapas para V2 completa

ordem recomendada; detalhes e critérios em `docs/additive/ROADMAP-V2.md`.

- [aberto] E1 · fechar catálogo executável: agentes, tiers, modelos, variantes,
  permissões, MCPs, ownership e equipes; aplicar D-037.
- [aberto] E2 · completar provas do runtime: composição, precedência, shell,
  verificações, limites compartilhados e fallback dentro da família.
- [aberto] E3 · validar capacidades: Sequential Thinking, RTK e MarkItDown;
  manter Exa desligado até necessidade comprovada.
- [aberto] E4 · executar piloto representativo nos quatro principais, com
  delegação, revisão de diff/branch e verificação pelo responsável.
- [aberto] E5 · validar vault e continuidade sem importar dados pessoais.
- [aberto] E6 · resolver ou delimitar sessões, equipes e mensagens no Zed/ACP.
- [aberto] E7 · inventariar e migrar seletivamente capacidades legadas provadas.
- [aberto] E8 · release candidate, versionamento, rollback e autorização para
  eventual substituição global.

dependências: E1 bloqueia E2; E2 e E3 bloqueiam E4; E4 bloqueia E7/E8. E5/E6
podem avançar em paralelo após os contratos de E1. nenhuma etapa libera troca
global antes de E8.

## manutenção por rodada

- [feito] regressão local de regras resolvidas adicionada em
  `scripts/check-v2.py`: antes do patch, 60 falhas (cinco caminhos sintéticos
  em cada um dos 12 subagentes); depois, 16 agentes e zero falhas. `read: allow`
  posterior aos denies do topo os anulava; substituído por mapa com bloqueios
  explícitos nos subagentes. corrige a interpretação anterior de que presença
  das regras no merge bastava. nenhum arquivo protegido lido, nenhum modelo
  invocado. teste simula globs simples da configuração resolvida, não prova
  sandbox, bloqueio de shell ou cobertura de todos os caminhos possíveis.
- [aberto] ampliar provas para caminhos absolutos, ferramentas de busca e shell;
  os bloqueios de `read` não equivalem a isolamento de processo. reiniciar a
  sessão V2 para carregar os frontmatters corrigidos.
- delegações `capabilities-local` e `regression-local` encerradas após falha de
  renovação Claude no runtime legado, informada pelo usuário; sem entregas
  encontradas nos scripts/relatórios previstos. lead retomou execução direta.

- [feito] revisão documental R2: lidas as duas fontes históricas locais, comparação
  amostral independente com corpus e leitura direta do código oficial `v1.18.30`
  (`llm.ts`, `llm/request.ts`, `system.ts`, prompts Astra/Anthropic/default).
  proposta refinada com fase/aceite, continuidade, delegação e gatilhos sob demanda.
  evidências e rejeições em `docs/additive/PROMPT-READINGS.md`; sem ativação.
- [feito] R3: usuário aprovou 1A/2A/3A; decisões D-025–D-027, contrato e
  operate alinhados. Leader escreve coordenação, verificações admitem artefatos
  regeneráveis delimitados, base própria preserva contratos necessários do harness.
- [feito] preparado roteiro de validação isolada R3 em PROMPT-PROPOSAL.md;
  preparação documental, sem execução ou ativação.
- [aberto] avaliar R3 contra baseline nativo em cenários controlados; medir
  qualidade, violações, custo e latência. R1/R2 apenas com snapshots fiéis.
  Comprovar composição por modelo e controles dos limites aprovados do Leader
  antes de ativar; escolhas de produto fechadas não equivalem a controles testados.

- [feito] revisão documental R1 de `docs/additive/PROMPT-PROPOSAL.md` contra
  contrato/decisões: removidas duplicações entre camadas, Tasker generalista,
  Coder independente de Leader, rastreabilidade e matriz de controles efetivos.
  contrato alinhado à correção explícita do Tasker. nenhuma ativação ou teste
  runtime; leitura restante do corpus continua pendente.

- [feito] corpus público clonado com autorização para `prompt-reference/`,
  ignorado no projeto; leituras e proposta documentadas por subagente Task.
  lead corrigiu conflitos de precedência, dependência artificial do Leader e
  exceção indevida de acesso a segredos. validação documental, não runtime;
  leitura integral ainda pendente por limites operacionais/truncamento.

- [feito] contrato consolidado e índice alinhado aos arquivos reais; corrigido
  status do vault para desenho aprovado (D-022), piloto não validado. nenhuma
  configuração/runtime alterado. próximo: catálogo enxuto e permissões dos agentes.

- [feito] 2026-09-10: pesquisa documental dos quatro componentes e matriz por
  arquétipo concluídas por dois agentes; fontes e comandos extraídos em
  `docs/additive/CAPABILITIES-2026-09-10.md`. não houve teste funcional,
  instalação ou migração; inventário do runtime segue pendente.
- checkpoint autorizado: avaliação registrada para retomada após compactação;
  naquele momento composição/exposição aguardavam resposta; superado por D-006–D-010.

- [feito] 2026-09-11: escolhas da rodada consolidadas em D-006–D-021; políticas
  desejadas separadas de suporte efetivo. sem instalação, ativação ou mudança
  global. pesquisa de sessões permanece bloqueada, sem resultados técnicos.

- [feito] 2026-09-11: concluída pesquisa pública de sessões e revisão de escopo;
  registro anterior de bloqueio é histórico, superado pela retomada autorizada.
  nenhuma configuração/instalação alterada; D-021 continua não implementada.

- [feito] 2026-09-11: proposta de vault obsidian registrada
  (`docs/additive/VAULT-2026-09-11.md`); arquitetura (`docs/core/VAULT-ARCHITECTURE.md`),
  decisão D-022 (local/repo, md puro, agentes organizam automaticamente,
  sem auditoria obrigatória), piloto `vault/` e script `scripts/import-notion-zip.sh`
  criados; `n2o` binário baixado `.opencode-local/bin/n2o`. nenhuma execução
  de migração; validação com agentes ainda pendente.

- [feito] 2026-09-11: importado zip do Notion (Markdown & CSV) via
  `scripts/import-notion-zip.sh`: 24 arquivos `.md`, 7,0M total, sem normalização.
  correção de escopo: export é de uso pessoal, movido de `vault/fontes/` para
  `pessoal/notion/`, fora do vault dos agentes; `pessoal/` ignorado no git por
  padrão. `vault/fontes/` voltou a ficar vazio.

- [feito] 2026-09-11: organizado `pessoal/notion/`: 25 renames (24 `.md` + 1 `.csv`),
  removidos sufixos de ID do Notion e corrigido mojibake cp866→utf-8 nos nomes
  (`Diferenças`, `Herança`, `Normalização` etc.); wrapper `Export-*/` achatado;
  links internos `.md` reescritos junto (12 links válidos, 0 quebrados).
  links `.csv` para views não exportadas seguem pendentes no Notion.

- [feito] 2026-09-12: mapeada a integração real da 1.18.30
  (`docs/additive/INTEGRATION-1.18.30.md`) e auditada a base isolada
  (`docs/additive/AUDIT-ISOLATED-2026-09-12.md`): base limpa, 7 agentes nativos,
  1 skill built-in, 0 MCP/plugin/credencial.

- [feito] 2026-09-12: construída a configuração `v2/` e apontado o launcher para
  ela. evidência observável: `debug config` resolve `instructions: ["kernel.md"]`,
  `default_agent: coder`, 2 MCPs desligados e 16 agentes próprios; `debug agent`
  confirma enforcement — reviewer sem `edit/write/task/webfetch/todowrite/skill`
  e bash só leitura git; explorer sem bash e sem `apply_patch`; coder-* sem
  `task` e com `git push/commit`, `gh`, `sudo`, `rm -rf` negados; leader com
  escrita restrita a `docs/**` e `vault/**`; `question` liberado nos principais;
  `tasker` com `external_directory` amplo. correção aplicada: `~/projects/**`
  expandia para o HOME isolado e foi substituído.

- [feito] 2026-09-12: revisão de segurança da config (agente dedicado, somente
  leitura): 0 crítico, 2 altos, 3 médios. corrigidos: `leader` passou a `bash`
  deny por padrão com allowlist de inspeção/verificação e `skill: deny`; `rtk *`
  aberto foi fechado (não permite `rtk proxy <cmd>`); `coder/tasker/designer`
  ganharam deny para `/usr/bin/sudo*`, `/bin/sudo*`, `env sudo*`, `doas*`,
  `su -*`, `sg *`, `rm -r*`, `rm --recursive*`, `rm -fr*`; revisores perderam
  `bash` por completo (evita `git diff --output=` criar arquivo); `tasker` passou
  de `external_directory` amplo para `/home/dasher/**` com deny em `.ssh`,
  `.gnupg`, `.aws` e nos diretórios do OpenCode legado. adicionado `permission`
  de topo negando leitura de `pessoal/**`, `conversa*.json`, `.env*` e
  `auth.json` — confirmado por `debug agent` que o topo MERGE com o por-agente.
  achado MÉDIO-1 (agentes não carregariam) foi refutado por evidência própria.
  risco residual aceito e documentado: verificação executa código do projeto
  (`npm test`, `npm run build`, `pytest`, `tsc`), então o Leader pode disparar
  scripts arbitrários definidos pelo repositório; exclusividade de equipes ao
  Leader (D-013) continua sem enforcement nativo.

- [feito] 2026-09-12: injeção de contexto provada em sessão real com o modelo
  gratuito `opencode/nemotron-3.5-lightning-free` (sem credencial própria).
  método: marcador temporário em `v2/kernel.md` e em `AGENTS.md`, pergunta pelos
  marcadores, restauração verificada. primeira rodada devolveu só o marcador do
  kernel; o do projeto veio `NAO-ENCONTRADO`. causa lida no código oficial
  `session/instruction.ts`: a descoberta nativa de `AGENTS.md`/`CLAUDE.md` está
  condicionada a `!OPENCODE_DISABLE_PROJECT_CONFIG`, e o launcher fixava esse
  flag — D-012 estava violada na prática. correções: flag removido do launcher e
  `instructions` passou a caminho absoluto de `v2/kernel.md` (funciona nos dois
  modos de resolução). segunda rodada devolveu os dois marcadores. `export` de
  sessão não serve de prova: traz `info` e `messages`, não o system.
  risco residual novo: com project config habilitado, `opencode.json`/`.opencode/`
  de um projeto-alvo mescla e pode sobrepor permissões e agentes da V2.

- [feito] 2026-09-12: `agent list` confirma que `build`, `plan`, `general` e
  `explore` desaparecem com `disable: true`; restam os 4 principais, os 12
  subagentes e os 3 internos (`compaction`, `summary`, `title`).

- [feito] 2026-09-12: OpenAI OAuth autenticado; `models` expõe famílias OpenAI e
  Anthropic. `gpt-5.6-luna` foi provado em execução primária e em delegação.
  `gpt-5.4-mini` e `gpt-5.4` foram rejeitados pelo Codex com conta ChatGPT
  apesar de listados; agentes GPT leves foram alinhados ao Luna low e Coder II
  ao Luna medium. Astra foi provado no reviewer; variantes Claude ainda não
  têm credencial válida.
- [feito] 2026-09-12: piloto mínimo de delegação passou: `coder`/Luna low usou
  `task`, `explorer-gpt`/Luna low contou `docs/core/*.md` e retornou
  `DELEGADO=4`. prova cobre dispatch, modelo válido e retorno, não revisão,
  alternância ou fluxo completo de verificação.
- [feito] 2026-09-12: `leader`/Luna low delegou uma revisão somente leitura ao
  `reviewer-gpt`/Astra high; o subagente confirmou a seção do backlog e retornou
  o achado correto. prova cadeia Leader→reviewer, modelo Astra e escopo sem
  edição; não prova revisão de diff real nem execução de verificações.
- [aberto] piloto completo de revisão/alternância: delegação GPT/Claude e revisão
  read-only já passaram; alternância automática, revisão de diff real e
  verificação coordenada ainda não foram provadas.
- [feito] 2026-09-12: `op-anthropic-auth@0.1.4` auditado e fixado no `v2/`; o
  launcher deixou de usar `OPENCODE_PURE=1` para permitir esse único plugin
  declarado. `debug config` mostra `plugin_origins` com a versão fixada; cache e
  auth continuam sob `.opencode-local/`. nenhuma credencial foi lida ou criada.
- [feito] login OAuth Anthropic e piloto Claude concluídos; a credencial API
  antiga não foi removida, mas não é usada enquanto o OAuth estiver válido.
- [feito] 2026-09-12: usuário concluiu OAuth Anthropic; `providers list` confirma
  Anthropic e OpenAI como `oauth`. chamada Haiku respondeu
  `AUTH_ANTHROPIC_OK`; `coder`/Sonnet delegou ao `explorer-claude`/Haiku e
  recebeu `DELEGADO_CLAUDE=sim`. piloto GPT+Claude básico fechado.
- [feito] 2026-09-13: capacidades locais E3 instaladas e validadas:
  - RTK 0.49.0 em `.opencode-local/tools/rtk/`, wrapper `scripts/rtk-local.sh`
    e entrypoint `scripts/bin/rtk`. config persistente em
    `.opencode-local/tools/rtk-runtime/config/rtk/config.toml` bloqueia
    tracking/retriever/telemetry/hooks; allowlist de comandos RTK e rejeição de
    `proxy`, `init`, `--config`, opções globais; `rtk run` disponível para saída
    bruta; sem persistência de saída integral; entrypoint `scripts/bin/rtk`.
  - MarkItDown 0.1.6 em venv `.opencode-local/tools/markitdown-0.1.6/venv/`,
    wrapper `scripts/markitdown-local.py`, entrypoint `scripts/bin/markitdown`.
    CLI só aceita arquivo local existente; rejeita URI, stdin, plugins, URLs.
    nenhum plugin instalado; não é sandbox de processo.
  - evidência em `docs/additive/CAPABILITIES-LOCAL.md`; testes sintéticos
    passaram; latência/perda em formatos maiores pendentes; download/instalação
    sem sudo, sem credenciais, sem instalação global, sem alterar launcher/v2/.
- [feito] 2026-09-13: matriz completa de agentes em `docs/additive/AGENT-MATRIX.md`
  (16 agentes: modo, família, variante, task, shell, edit/write, MCP, ownership);
  deriva de `v2/agent/*.md` + `debug agent`; risks: shell bypass, MCP por agente,
  exclusividade equipes sem enforcement.
- [feito, cobertura parcial] 2026-09-13: `scripts/check-v2.py` PASS (16 agentes,
  0 falhas); verifica exemplos de regras resolvidas de leitura, delegação e
  ferramentas, e fixture de precedência. não prova busca, normalização de caminhos
  absolutos nem bloqueio de shell. alegação anterior corrigida na revisão R-02.
- [feito] 2026-09-13: fallback D-037 confirmado **não suportado nativamente** na
  1.18.30 (Context7 + código oficial: retry mesmo modelo, subagente falha propaga
  erro, sem fallback cross-model); registrado como "não suportado".
- [parcial, histórico] 2026-09-13: prova inicial do vault criou notas e rodou
  detector; não houve fusão automática. a saída antiga dizia 7 links, mas contava
  notas. contagem e piloto de protocolo corrigidos na rodada R-03/R-04 abaixo.
- [feito] 2026-09-13: limites attach/sessões documentados em
  `docs/additive/SESSION-LIMITS.md`. decisão: `acp` no Zed mantido; `attach`,
  mensageria inter-sessão, visibilidade filhos/equipes, Ensemble fora da V2
  inicial. D-021 permanece não implementada.

- atualizar o status de cada item tocado, a evidência observável e novas
  dependências; manter itens concluídos como histórico curto.

## revisão da rodada · 2026-09-13

- [feito] revisão independente de configuração/capacidades e validação pelo
  lead; evidências: `docs/additive/REVIEW-2026-09-13.md`. checker repetiu
  16 agentes/0 falhas, mas probes demonstraram lacunas. nenhum código corrigido.
- [feito] R-01 (alto): `gh pr merge*` exige `ask` em Coder/Tasker/Designer;
  checker central confirmou os mapas resolvidos, sem executar `gh`.
- [feito] R-02: diagnóstico falha fechado e sanitizado; fixture exige agente
  customizado e baseline; estado de falhas reinicia por execução. 13 testes OK.
- [feito] R-03: inventário por caminho, homônimos, corpo integral normalizado,
  exclusão de exemplos de código, contagens e status corrigidos. 9 testes OK;
  revisão final incluiu extensão explícita `.md` e escape de controles na saída;
  após piloto: 8 notas, 25 links, 0 grupos duplicados. detector não funde notas.
- [parcial] R-04: índice preenchido; Terra novo recuperou 3 notas via índice
  (1 nota/consulta), criou procedimento/indexação e supersedeu rascunho sintético
  preservando o original. piloto de protocolo aprovado no agente orquestrado,
  não prova automação integrada à V2 nem deduplicação automática. integração
  funcional completa na V2 permanece pendente; piloto incremental do usuário abaixo
  já demonstra delegação, uma consulta e escrita com correção de links.
- [feito] R-05: shell e Python forçam `ORT_DISABLE_TELEMETRY=1` antes do import,
  inclusive ambiente herdado com `0`; 5 testes sintéticos centrais OK. sem conversão
  real nova nem captura de tráfego; não é garantia de ausência geral de egress.
- [feito] R-06: LOGIC, matriz e limites reconciliados com configuração ativa,
  cobertura parcial e evidência histórica ACP; referência inexistente deixou de
  ser fonte. D-037 permanece mesma família; nenhuma nova decisão criada.
- [bloqueado] release/E4: integração funcional do vault e demais aceites amplos
  continuam pendentes. piloto com provedores e substituição global dependem das
  respectivas autorizações; correções locais não equivalem a release aprovada.

### regressão das correções

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_*.py'`:
  27 testes OK na regressão final. mensagens BROKEN/AMBIGUOUS/DUPLICATES são
  cenários negativos esperados.
- `TMPDIR=/tmp/opencode PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-v2.py`:
  16 agentes, 0 falhas; avisos shell preservados. memória antes da regressão final:
  2,8 GiB disponíveis.
- `python3 scripts/vault-links.py`: após a separação `vault/agents`/`vault/human`,
  14 notas, 29 links, 0 grupos duplicados, exit 0.
- `sh -n opencode-isolated scripts/rtk-local.sh scripts/markitdown-local.sh`: exit 0.
- evidência detalhada e trajetória do piloto: `docs/additive/REVIEW-2026-09-13.md`.
  sem build/typecheck, commit, publicação, privilégio ou mudança global.

### piloto V2 executado pelo usuário · 2026-09-13

- [feito] transcrição local fornecida pelo usuário inspecionada, sem incorporar
  seu conteúdo integral: Coder/Terra chamou `task` com `explorer-gpt`; retorno
  completed identificou `AGENTS.md` como canônico. não foi delegação simulada.
- [feito] uma consulta recuperou `procedimentos/validacao-v2.md` após índice e
  busca pelo nome. as outras duas consultas não aparecem nesta transcrição.
- [feito] escrita restrita aos dois `piloto-v2.md` (inbox/procedimentos) e índice;
  primeiro patch criou links ambíguos, segundo corrigiu com paths e aliases.
  usuário capturou falha e sucesso; lead repetiu validador: 10 notas, 30 links,
  0 grupos duplicados, exit 0.
- [parcial] nota inbox foi criada diretamente como `superado`, junto da substituta;
  demonstra representação do resultado, não transição de rascunho preexistente
  nem resolução de sobreposição de conteúdo. R-04 continua parcial nesses aceites.
- [pendente] repetir as duas consultas restantes e promover rascunho preexistente
  com sobreposição controlada. automação permanente, `team_spawn`, navegação visual
  de filhos e comunicação intersessão não são comprovados por esse piloto.

### sessões independentes e progresso Zed · 2026-09-14

- [feito] usuário esclareceu: descobrir/comunicar com sessões independentes como
  mensagem de usuário; não restringir a filhos/equipe. progresso Zed deve aparecer
  sem perguntar ao agente; navegação completa de filhos não é requisito mínimo.
- [feito] pesquisa paralela de código público concluída, sem teste runtime:
  `docs/additive/INTERSESSION-PROGRESS-2026-09-14.md`. API aceita prompt por ID sem
  parentesco; descoberta/autorização global e entrega a ocupado não estão resolvidas.
  progresso Ensemble observado no código usa TUI/dashboard; ACP não o traduz.
- [histórico] S-01: identificar versões no ambiente do sintoma e delimitar descoberta
  entre projetos/processos, autorização e tratamento de sessão ocupada. não ativar
  exposição irrestrita nem confundir disponibilidade HTTP com autorização.
- [histórico] S-02: propor menor integração de estado da equipe com ACP da sessão
  principal; aprovar escopo antes de instalar plugin/alterar adaptador.
- [histórico] S-03: prova A/B independentes (livre/ocupada/alvo não autorizado) e
  prova Zed (início/atividade/conclusão/erro sem pergunta). chamadas a modelo e
  mudanças de ambiente exigem autorização específica; nenhuma feita na pesquisa.
- o escopo anterior fora da V2 inicial permanece histórico, não veto ao novo
  pedido de investigação. nenhuma arquitetura nova foi aprovada nesta rodada.
=== BACKLOG S-01 / S-02 / S-03 registro rápido ===
- [histórico] S-01 intersessão: descoberta global/autorização e entrega ocupada
  ainda sem implementação; supersedido pela ponte local abaixo, sem federação.
- [histórico] S-02 progresso Zed: lacuna TUI→ACP comprovada; supersedido pela
  ponte local abaixo, com confirmação visual ainda necessária.
- [histórico] S-03 piloto mínimo: A/B intersessão + progresso Zed; supersedido
  pelos smokes locais abaixo; Zed continua pendente.
- [parcial, smoke ACP + validação manual] S-04: plugin V2 expõe `sessions_list`, `sessions_send` e
  `sessions_receive`, com sessões vivas registradas por processo, origem
  identificada, destino validado e recibos de resposta. A/B real no launcher ACP
  confirmou aviso e marcador recebidos; porém `conversa-sessoes-2026-09-15.md`
   mostra que as sessões Zed do usuário foram depois migradas para o launcher
   local; os exports Y/Z comprovaram send/receive/reply. não é federação global
   nem entrega FIFO.
- [parcial, smoke ACP + validação manual] S-05: plugin expõe `team_spawn` via
   `session.create` + `promptAsync`; ponte local traduz progresso para
   `agent_message_chunk` fora de Thinking, com estados queued/starting/busy/idle
   e erro. usuário confirmou visualmente atividade e finished no Zed; wake
   automático do pai e spinner contínuo ainda não têm prova ponta a ponta.
- [feito] documentação operacional: README raiz criado com instruções de patch
  reproduzível, configuração Zed, contrato de segurança, comandos de validação,
  smokes, limites e rollback. a animação exata do spinner continua aceite visual
  do cliente, não promessa da implementação.
- [feito, catálogo] removido `OPENCODE_DISABLE_MODELS_FETCH` do launcher V2;
  `./opencode-isolated models --refresh --verbose` concluiu com `Models cache
  refreshed` e 38 IDs listados. Muse/Nemotron/Luna/Terra/Sol/Astra/Opus/Sonnet
  aparecem; `Inkling` não apareceu no catálogo público desta execução. isso não
  prova acesso/autorização de cada provider nem deve ser confundido com a lista
  de favoritos do Zed.
- [feito, restart-only] `/subconfig` foi exposto ao ACP/Zed por
  `.opencode/command/subconfig.md`; `subconfig reload` indexa providers/modelos
  e `/subconfig <agent> <provider/model> <effort>` grava overrides em
  `v2/subagent-models.json`. aliases `coder-basic/plus/pro`, validação de IDs,
  normalização `xh`/pontuação e rejeição de effort ausente cobertos por 10 testes
  Node. `task` e `team_spawn` agora usam agentes pré-configurados; spawn não
  aceita modelo arbitrário do pai. a mesma tool pode ser chamada diretamente
  pelo agente atual, sem slash command, conforme instrução adicionada ao kernel;
  aplicação requer restart.
- [feito, validação visual parcial] progresso operacional de `team_spawn` foi movido de
  `agent_thought_chunk` para `agent_message_chunk`, porque o Zed recolhia o
  primeiro dentro de “Thinking”. smoke automatizado cobre o novo tipo; usuário
  confirmou status fora de Thinking; spinner contínuo ainda depende do Zed.
- [feito, validação automatizada] eventos de estado do filho passaram a carregar texto;
  a ponte agora pode mostrar `working`, `finished` e `failed`, em vez de
  descartar os eventos `starting/busy/idle/error` sem payload textual.
- [parcial, validação automatizada] estados terminais `idle/error` agora acordam o pai ocioso por
  prompt interno fixo; durante turno ativo ficam pendentes até o turno terminar.
  conteúdo do filho não é interpolado no prompt.
- [feito, validação automatizada] flood de `Subagent finished` corrigido: o
  progresso de ciclo de vida do filho passou a ser monotônico
  (`starting < busy < idle`, `error` uma vez). antes, `session.status` oscilando
  busy/idle e `session.updated` reinjetando `starting` passavam pelo dedup de
  estado imediato e geravam uma mensagem por passo do subagente. evidência:
  `node --test scripts/test_session_bridge.mjs`, 8/8, incluindo a regressão
  "status oscilante do filho não repete progresso de ciclo de vida" (5 rodadas
  de updated/busy/idle produzem 1 evento de cada estado). não altera o contrato
  de eventos nem o transporte ACP.
- [congelado, D-041] integração ACP/Zed sai do caminho ativo: `scripts/acp-bridge.py`,
  `scripts/test_acp_bridge.py`, `scripts/s04_smoke.py`, `scripts/s05_smoke.py` e o
  branch `acp` de `opencode-isolated` permanecem no repositório, continuam
  passando e podem ser usados, mas não recebem evolução. o alvo operacional
  passa a ser o TUI. não remover sem antes resolver: (a) `events/` só tem
  consumidor e coletor no proxy — sem ele os eventos escritos por `emitEvent` e
  pelo mail nunca são apagados; (b) o wake automático do pai vive em
  `_inject_internal_prompt`, no proxy, e não tem equivalente TUI; (c) S-04/S-05
  perdem seus únicos smokes ponta a ponta. as tools `sessions_list/send/receive`,
  `team_spawn` e `subconfig` NÃO são ACP-específicas e seguem ativas no TUI.
- [feito] reformatar kernel e prompts de agente para o OpenCode TUI: executado e
  detalhado na entrada de reforma dos prompts abaixo; esta linha ficou obsoleta.
- [feito, D-042] prioridade 1 do harness fechada como decisão e aplicada: `v2/kernel.md`
  §6 passou a definir conclusão por afirmação/alvo/camada/ambiente, com a regra
  "não deixe um estágio anterior passar por posterior" e a triagem de causa; e a
  distinção entregue (agente, com evidência) × fechado (usuário), explicitamente
  sem cobrança de validação a cada passo. `v2/agent/leader.md` ganhou a
  conferência de faixas/totais de leitura delegada apenas em conclusão crítica.
  originais em `docs/additive/prompt-backup-2026-09-16/` porque o diretório não
  é repositório git. evidência: `debug config` e `debug agent leader` OK.
- [aberto, aceite de D-042] executar os três cenários sanitizados que provam a regra:
  (1) job exportado e nunca chamado, com guarda por import dando verde;
  (2) teste adaptado para produzir verde sobre defeito real do produto;
  (3) delegado alegando leitura até EOF com faixa impossível. critério: o agente
  detecta e nomeia a confusão de camada sem ser avisado. sem isso, D-042 é regra
  escrita, não regra provada.
- [feito] lacuna de corpus fechada: a iteração anterior de um dos projetos
  primários foi lida diretamente
  (`HARNESS-CORPUS` §PL, `HARNESS-COMPARATIVO` §11). não inverte conclusões;
  eleva a prioridade 3, porque o usuário já mantém à mão escada de precedência,
  ata de conflito com vencedor declarado, registro de revogadas e pendências com
  causa. o harness deve adotar esse formato, não inventar outro.
- [feito, validação por configuração resolvida] reforma dos prompts para o alvo TUI:
  (1) CORRIGIDO na mesma rodada: a linha comum dos 10 agentes foi removida por
  engano e restaurada. ela não é preâmbulo redundante — é a camada `system fino`
  de `additive/PROMPT-PROPOSAL.md`. como `request.ts` da `v1.18.30` escolhe
  `agent.prompt` OU `SystemPrompt.provider(model)`, o prompt de agente substitui
  o baseline do provedor: essa linha é o topo do system prompt efetivo, não
  decoração. lição registrada: texto repetido em todos os papéis pode ser camada
  compartilhada, não duplicação;
  (2) kernel deixou de citar Exa, que está `enabled: false`;
  (3) regras de vault e de escrita indireta saíram do kernel para `AGENTS.md`,
  devolvendo agnosticidade ao núcleo;
  (4) entraram três regras que a varredura recomendou e nunca haviam sido
  aplicadas: verificar vigência antes de tratar conflito como pergunta aberta;
  delegação não transfere autorização nem comprova capacidade, e relato de
  delegado é dado, não evidência; o que se repete vira teste ou procedimento,
  não parágrafo permanente;
  (5) `explorer` e `summarizer` ganharam contrato de saída derivado das falhas
  reais desta V2 — inventário não é leitura, EOF não garante ausência de
  truncagem, faixa relatada precisa caber no total, cobertura declarada precisa
  ser a real.
  evidência: `debug config` OK; `debug agent` resolve os 10 agentes sem
  preâmbulo; `check-v2.py` 10 agentes/0 falhas; 38 testes Python e 11 Node.
  originais em `docs/additive/prompt-backup-2026-09-16/`.
- [feito] `scripts/export-prompts.py` gera `docs/PROMPTS.md` a partir da
  configuração resolvida pelo launcher, não do texto dos arquivos: o export
  mostra modelo e effort realmente vigentes, incluindo overrides de `subconfig`.
  não reproduz prompt interno da plataforma. regenerar após mudar kernel ou
  agente.
- [aberto] provar localmente a substituição do system prompt: hoje a afirmação de
  que `agent.prompt` suprime `SystemPrompt.provider(model)` vem de leitura do
  código da `v1.18.30`, não de inspeção do payload realmente enviado ao modelo.
  enquanto não houver essa prova, `docs/PROMPTS.md` declara o limite em vez de
  afirmar cobertura.
- [feito, D-043] DCP instalado nesta V2: `@tarquinen/opencode-dcp@3.1.15` no
  `plugin` de `v2/opencode.json`, com `v2/dcp.jsonc` derivado de D-042 — as
  ferramentas que produzem evidência (`read`, `grep`, `glob`, `list`, `bash`,
  `webfetch`) entram nas listas de proteção, porque os defaults do plugin não as
  cobrem. evidência: `debug config` expõe `primary_tools: ["compress"]` e o
  command `dcp-compress`; `debug agent tasker` mostra `compress: true` e 17
  ferramentas; pacote resolvido em `.opencode-local/cache/opencode/packages/`,
  nunca global; `check-v2.py` 10 agentes/0 falhas e 38 testes Python OK.
- [parcial, aceite de D-043] proteção exercitada em sessão real: duas compressões
  desta sessão (250 mensagens no total) mantiveram as saídas de `read`, `grep` e
  `bash` disponíveis, sem virar placeholder. isso prova a lista de proteção e a
  substituição por sumário. continua **não** provado: (a) o caso adversário, em
  que a poda tentaria descartar a saída de um teste e seria barrada; (b) a poda
  automática — `deduplication` e `purgeErrors` rodam em recálculo próprio e não
  foram exercitados; (c) o efeito no cache de prompt, que o próprio projeto
  estima em ~85% contra ~90% sem DCP.
