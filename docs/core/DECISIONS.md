# decisions · opencode prefs v2

| id | decisão | resposta/estado | impacto |
| --- | --- | --- | --- |
| D-001 | base de execução isolada | feito: launcher local `1.18.30` com estado em `.opencode-local/` | evita herdar config, plugins, skills e autenticação legados por padrão. |
| D-002 | arquitetura documental | decidido nesta rodada | `core` guarda contratos; `additive` guarda contexto e material temporário. |
| D-003 | estrutura canônica | decidido nesta rodada | backlog registra todo trabalho e histórico; decisions registra respostas; logic registra funcionamento. |
| D-004 | instrução única para agentes | solicitado pelo usuário em 2026-09-10: compor instruções e linkar Claude | `AGENTS.md` canônico na raiz; `CLAUDE.md` é symlink relativo para `AGENTS.md`, sem duplicação. |
| D-005 | abrangência das capacidades | usuário escolheu todos os usos e incluiu MCPs como capacidades, citando Exa Search, RTK, MarkItDown e Sequential Thinking para avaliação transversal | avaliar acesso pelos arquétipos; não autoriza instalação, chamada obrigatória ou exposição permanente de todas as ferramentas. RTK é CLI, não MCP. |
| D-006 | composição | Exa + Sequential Thinking via MCP; RTK + MarkItDown via CLI | composição aprovada para validar, não instalação automática. |
| D-007 | exposição | Exa e Sequential Thinking disponíveis aos três especialistas; conjuntos fixos provisórios | preferência continua sendo sob demanda; verificar suporte real e efeito sobre contexto, sem criar carregador especulativo. acesso de subagentes e do Leader ainda será detalhado. |
| D-008 | rede e conversão | Exa pode pesquisar conteúdo público sem confirmação; MarkItDown só converte arquivos locais fornecidos/indicados na tarefa | não enviar código privado, logs internos, dados pessoais ou segredos; sem varredura de pastas, plugins ou serviços externos na conversão. |
| D-009 | RTK | padrão forte para comandos compatíveis, uso explícito sem hook; telemetria desativada e sem persistir saídas completas | comando original somente por necessidade justificada; não substitui obrigatoriamente ferramentas nativas. validar configuração efetiva; nunca repetir automaticamente ações com efeitos para recuperar saída. |
| D-010 | Sequential Thinking | uso seletivo com ênfase em investigação, hipóteses, erros e correções; logging desativado | objetivo de raciocínio assistido, não garantia de qualidade; conclusões exigem evidências. |
| D-011 | composição de instruções | reconstruir enxuto: system prompt + kernel comum + operate especializado + AGENTS.md + contexto da tarefa | objetivo de integração e deduplicação; ordem e extensão reais ainda precisam ser verificadas. sem fork/alteração do binário; no máximo patches independentes de detalhes de versão, sempre revalidados. |
| D-012 | instruções de projeto | carregar AGENTS.md pelo mecanismo nativo, sem reinjeção nem herança global legada | ainda não habilitado no launcher isolado. |
| D-013 | principais | seleção manual nativa, nomes funcionais sem personalidade; Coder, Tasker, Designer e retorno de Leader | substitui a escolha intermediária de excluir Leader. Leader coordena e faz revisão mestre; nunca implementa ou corrige. demais podem delegar subagentes comuns; exclusividade de equipes ao Leader é o desenho em discussão, confirmar no fechamento de permissões. |
| D-014 | autonomia | ações locais pertinentes à tarefa sem confirmação rotineira; ações destrutivas, privilegiadas, publicação/deploy e envio privado exigem autorização específica | não permite acesso a segredos; instalação local de dependências necessárias admitida na política futura, com YAGNI forte: reutilizar existente/nativo e evitar custo e abstrações especulativas. |
| D-015 | memória | documentação do projeto primeiro, sem memória global automática na base | memória compartilhada fica para avaliação posterior. |
| D-016 | modelos | principais sem modelo fixo; subagentes com modelo fixo por função/nível e variantes GPT/Claude | Coder I/II/III por complexidade e risco; busca/leitura e resumo podem ter tier único. Haiku e Luna são candidatos; catálogo/modelos concretos pendentes. |
| D-017 | alternância de família | uma tentativa alternativa automática controlada por limite/indisponibilidade ou falha na tarefa | respeitar restrições de família/cota do usuário, transmitir evidências e preservar estado; não repetir efeitos sem inspeção. mecanismo ainda não validado. |
| D-018 | revisão e verificação | revisores dedicados inspecionam escopo explícito (diff, branch, commits ou revisão completa), reportam e não editam nem executam verificações | verificações passam pelo principal responsável: Leader em equipes, agente-pai em delegações comuns; sem confirmação humana rotineira, com informação de andamento. Leader pode executar verificações na revisão mestre. |
| D-019 | conclusão e recursos | unidade de validação definida pelo projeto e mutável; terminado significa implementado e funcionando com evidência | menor escopo tecnicamente válido, contratos locais e limites globais; checagem parcial não prova o todo. coordenar execução/local exigido e recursos sem concorrência indevida. |
| D-020 | Git | política desejada da V2 permite commits locais automáticos após validação; push, PR e merge somente por pedido explícito | preservar alterações alheias, não reescrever histórico; commit não é conclusão. não altera restrições superiores da sessão atual. |
| D-021 | sessões e mensagens | priorizar Zed sem excluir equipes: sessões do mesmo projeto visíveis, acessíveis e com mensagens entre elas, sem gate humano de comunicação | pesquisar soluções existentes e lacunas OpenCode/ACP/Zed; não presumir que mensagens de equipe equivalem a mensagens entre sessões independentes. |
| D-022 | vault obsidian | usuário confirmou: local no repo, markdown puro, agentes organizam automaticamente; sem auditoria periódica obrigatória | arquitetura proposta em `docs/core/VAULT-ARCHITECTURE.md`; piloto em `vault/` criado. decisão ainda não validada com agentes; não substitui docs do projeto. |
| D-023 | importação Notion | usuário pediu instalação do `n2o` normal; binário baixado localmente `.opencode-local/bin/n2o` | script `scripts/import-notion-zip.sh` criado para extração manual de zip Notion; não usa token. sem execução de migração; `n2o` ainda não testado com credenciais.

## fechamento R3 · 2026-09-12

aprovação explícita do usuário: “1. A. 2. A. 3. A.”

| id | decisão | resposta aprovada | impacto |
| --- | --- | --- | --- |
| D-025 | escrita do Leader | pode atualizar plano, backlog, evidências e status, registrar decisões já aprovadas e sincronizar acompanhamento autorizado | implementação, correção e alteração de requisitos continuam delegadas; proposta não equivale a aprovação. Refina D-013 sem permitir implementar a solução. |
| D-026 | efeitos de verificações do Leader | verificações pertinentes podem gerar artefatos locais regeneráveis: build, cache, cobertura e relatórios | não podem corrigir código automaticamente, atualizar snapshots de referência nem alterar dados/serviços compartilhados. Testes com efeitos sensíveis exigem isolamento comprovado ou autorização específica; gates superiores continuam vigentes. Refina D-018; revisores continuam sem executar. |
| D-027 | base própria de prompts | construir base comum própria, preservando apenas contratos necessários do harness, sem copiar baselines inteiros | instruções por modelo só entram por necessidade de compatibilidade ou benefício demonstrado em avaliação. Aprova estratégia, não substituição do prompt ativo antes dos testes; refina D-011. |

## rodada 2026-09-12 · execução

| id | decisão | resposta aprovada | impacto |
| --- | --- | --- | --- |
| D-028 | famílias disponíveis | usuário informou que Luna deixou de estar disponível para subagentes; usar Sonnet como família OpenAI-alternativa indisponível | catálogo de subagentes passa a ser fixado sobre modelos efetivamente acessíveis; a alternância de D-017 só vale entre famílias disponíveis no momento. |
| D-029 | condução da rodada | usuário autorizou o lead a decidir e delegar execução aos subagentes, fechando tudo que estiver na jurisdição do lead | o que depender de credencial, escolha de produto do usuário ou substituição global permanece fora e é reportado no fim. |

## regra de registro

- D-024 · usuário confirmou os quatro principais juntos na v1 e autorizou
  inferir detalhes técnicos a partir das respostas existentes, sem questionário
  repetido. consolidação em `docs/core/CONTRACT.md`; inferências não equivalem
  a capacidades validadas nem resolvem escolhas ainda abertas silenciosamente.

| D-030 | configuração V2 construída | 2026-09-12: `v2/` passa a ser o `OPENCODE_CONFIG_DIR` do launcher isolado; kernel único via `instructions`, 4 principais sem modelo fixo, 12 subagentes com modelo/variant fixos em pares GPT/Claude, agentes nativos `build`/`plan`/`general`/`explore` desabilitados, MCPs `exa` e `sequential-thinking` declarados e desligados | permissões passam a ser enforcement real (`debug agent` confirma ferramentas negadas), não texto. modelos concretos e injeção do kernel em sessão ainda dependem de autenticação. |

| D-031 | MCPs na base | 2026-09-12: usuário dispensou Exa por ora e autorizou baixar o Sequential Thinking | `sequential-thinking` habilitado via `npx` com `DISABLE_THOUGHT_LOGGING=true`; evidência: `mcp list` retorna `connected`. `exa` fica declarado e desligado, sem chave e sem OAuth. |

| D-032 | config de projeto reabilitada | 2026-09-12: era a única forma de cumprir D-012 (AGENTS.md nativo) | `OPENCODE_DISABLE_PROJECT_CONFIG` saiu do launcher e `instructions` virou caminho absoluto. o isolamento de config global/plugins/skills/auth continua; o preço é que `opencode.json`/`.opencode/` do projeto-alvo passa a mesclar e pode sobrepor permissões da V2. |
| D-033 | disponibilidade observada no piloto | 2026-09-12: OpenAI OAuth funciona com `openai/gpt-5.6-luna`; Anthropic está cadastrado como `api` e falhou com chave inválida | `explorer-gpt`, `coder-i-gpt` e `summarizer-gpt` usam `gpt-5.6-luna` (low); `coder-ii-gpt` usa Luna (medium). `gpt-5.4-mini` e `gpt-5.4` foram rejeitados pelo Codex com conta ChatGPT mesmo aparecendo em `models`; `gpt-6-astra` foi provado no reviewer. variantes Claude ficam indisponíveis até credencial Anthropic válida. |
| D-034 | piloto de delegação | 2026-09-12: `coder` em `gpt-5.6-luna` delegou ao `explorer-gpt` e recebeu `DELEGADO=4`; `leader`/Luna delegou ao `reviewer-gpt`/Astra e recebeu achado correto | ferramenta `task`, resolução dos agentes GPT, permissões read-only do reviewer e retornos funcionaram. não prova alternância automática, MCP usado em tarefa ou validação ponta a ponta. |
| D-035 | OAuth Anthropic experimental | 2026-09-12: usuário autorizou seguir com `op-anthropic-auth`; versão publicada fixada em `0.1.4` | plugin externo carregado somente no launcher isolado; `OPENCODE_PURE` removido, sem instalação global. pacote auditado: OAuth PKCE/refresh e auth provider Anthropic; não lê Claude Code credentials. login e chamada Anthropic ainda dependem de ação do usuário e aceitação do risco/termos da Anthropic. |
| D-036 | piloto Claude | 2026-09-12: Anthropic OAuth confirmado; chamada Haiku respondeu `AUTH_ANTHROPIC_OK`; `coder`/Sonnet delegou ao `explorer-claude`/Haiku e recebeu `DELEGADO_CLAUDE=sim` | variantes Claude e delegação Claude funcionam no ambiente isolado. não prova refresh após expiração, alternância automática ou tiers Claude II/III em tarefa complexa. |
| D-037 | fallback por família | 2026-09-12: usuário definiu que o fallback pode usar sempre outro modelo da mesma família do modelo-pai | GPT usa apenas GPT; Claude usa apenas Claude. a troca deve preservar escopo, estado, permissões e nível adequado; não fazer fallback cruzado automático. suporte efetivo/nativo ainda precisa ser validado. |
| D-038 | recebimento intersessão | usuário confirmou em 2026-09-15 manter `sessions_receive` como fronteira explícita; política de peer data também fica no kernel/prompt interno | o bridge pode acordar a sessão e mostrar aviso, mas o envelope só entra no contexto do agente via `sessions_receive`, preservando validação, receipt, reply e a distinção entre dado peer e autorização humana. |
| D-041 | integração ACP/Zed congelada | 2026-09-16: usuário migrou para o TUI e escolheu congelar, não remover | `scripts/acp-bridge.py`, seus testes, os smokes S-04/S-05 e o branch `acp` do launcher permanecem no repositório e continuam válidos, mas não recebem evolução. supersede a priorização de D-021 sem revogar o contrato intersessão. removê-los exigiria antes resolver o consumo de `events/` (hoje o proxy é o único leitor e coletor) e o destino do wake automático. |
| D-042 | evidência de conclusão | 2026-09-16: usuário aprovou (a) disciplina, não campos; (b) texto curto no kernel, sem skill; (c) conferência de leitura delegada só em caso crítico, no leader; (d) aceite por três cenários sanitizados | conclusão passa a se referir a afirmação, alvo, camada e ambiente, nunca a exit code, com a triagem produto/instrumento/ambiente/documentação/premissa. o agente pode declarar **entregue** com evidência e limites; **fechado** é exclusivo do usuário. proibido cobrar validação a cada passo ou tratar a ausência dela como bloqueio — foi o excesso de gate humano que inviabilizou harnesses anteriores. aplicado em `v2/kernel.md` §6 e `v2/agent/leader.md`. o aceite da própria regra ainda não foi executado. |
| D-043 | poda dinâmica de contexto | 2026-09-16: usuário autorizou instalar o DCP nesta V2 | `@tarquinen/opencode-dcp` fixado em `3.1.15` no `plugin` de `v2/opencode.json`, instalado no cache isolado, **nunca global**. Auditoria da versão publicada: integridade sha512 confere com o registry, publicação por GitHub Actions com OIDC e provenance SLSA, sem script de `postinstall`, sem `child_process` (todo `exec(` é `RegExp.exec`), e uma única saída de rede — `fetch` para `registry.npmjs.org` em `lib/update.ts`, que é o auto-update. Por isso `autoUpdate: false`: mantém a versão auditada e elimina o tráfego. `lib/auth.ts` lê `OPENCODE_SERVER_PASSWORD` apenas para autenticar no servidor local do OpenCode; o launcher não define essa variável. Configuração em `v2/dcp.jsonc`, lida por `$OPENCODE_CONFIG_DIR`. Tensão com D-042 tratada explicitamente: os defaults do plugin protegem `task/skill/todos` mas deixam `read`, `grep` e `bash` desprotegidos, que são justamente as fontes de evidência; essas ferramentas entraram em `compress.protectedTools`, `bash` também em deduplicação e purgeErrors, `turnProtection` ligado e `allowSubAgents` mantido em `false` para não podar contexto de delegado. Não prova ainda que a poda preserva evidência em sessão real. |

inclua uma decisão somente quando a escolha tiver sido respondida ou aprovada.
propostas e hipóteses pertencem a `docs/additive/` e não entram nesta tabela.

## catálogo unificado · 2026-09-16

- D-040: usuário determinou um agente por papel. Os doze subagentes pareados
  `-gpt`/`-claude` foram substituídos por `coder-basic`, `coder-plus`,
  `coder-pro`, `explorer`, `summarizer` e `reviewer`, cada um com um modelo.
  Motivo declarado: tornar a troca de modelo direta. Impacto: supersede a parte
  de D-016 que fixava variantes por família e torna D-037 inaplicável na prática
  — sem par por família, não existe alternância automática dentro da família;
  qualquer troca passa a ser explícita via `subconfig`. As permissões por papel
  foram preservadas: os arquivos `-gpt` e `-claude` eram idênticos fora de
  modelo/variant, verificado por `diff` antes da remoção. Padrões iniciais em
  Anthropic por causa do limite atual da assinatura GPT; não é decisão de
  provedor permanente.

## acesso temporário para varredura · 2026-09-16

- D-039: usuário autorizou “pode aplicar esse patch e depois tiramos”. Adicionado
  `external_directory` ao `explorer-gpt` apenas para os seis projetos externos
  autorizados na varredura, sob
  `/home/dasher/projects/`, com deny geral. Não concede escrita/shell, não altera
  outros agentes e não libera credenciais. Remover após a investigação; mudança
  exige restart. Configuração resolvida validada; leitura real ainda pendente.
- D-039 encerrada em 2026-09-16: a varredura foi executada e o bloco temporário
  foi removido; `debug agent` confirma o retorno ao padrão `ask`. A exceção não
  se estendeu a outros agentes nem a escrita, e não fica disponível por herança.
