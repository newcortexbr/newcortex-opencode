# leitura do corpus de prompts

status: pesquisa documental em andamento, com cobertura integral parcial comprovada; não é decisão do core, não ativa configuração e não prova comportamento do runtime.

## escopo e confiança

### revisão R2 · método e montagem oficial

Leitura direta até EOF das cópias locais `PLANO_MESTRE.md` (371 linhas) e
`PROCESSO_INICIO_PROJETO.md` (938 linhas). Preservadas sem edição. Pesquisa
independente amostral do corpus por subagente; não aumenta a contagem EOF
histórica, pois não houve reconciliação de paths. Um bloqueio externo reportado
pelo subagente para o processo não afeta a leitura local integral feita pelo lead.

Fontes oficiais lidas diretamente via raw da tag `v1.18.30` em
`https://raw.githubusercontent.com/anomalyco/opencode/v1.18.30/`:

- `packages/opencode/src/session/llm.ts`: delega montagem a LLMRequestPrep.
- `packages/opencode/src/session/llm/request.ts`, função `prepare`: escolhe
  `agent.prompt` em vez de `SystemPrompt.provider`; acrescenta `input.system`
  e `input.user.system`, concatena e chama `experimental.chat.system.transform`.
  OpenAI OAuth recebe `options.instructions`; o caminho comum cria mensagens
  system. Ordem textual não cria níveis independentes de autoridade.
- `packages/opencode/src/session/system.ts`: seleciona baseline pelo modelo;
  produz ambiente, catálogo de skills e instruções MCP separadamente.
- `packages/opencode/src/session/prompt/{gpt-astra,anthropic,default}.txt`:
  leitura integral dos três baselines, não de todos os modelos.

Context7 foi usado para localização, mas seus trechos de `dev` não foram usados
como prova de versão. Não houve execução do launcher, chamada de modelo de teste,
captura de payload, leitura de autenticação ou auditoria completa de `instruction.ts`.
Logo, isto comprova comportamento do código consultado, não a montagem local ativa.

| comparação | julgamento R2 |
| --- | --- |
| Astra: autonomia até conclusão, ferramentas dedicadas, testes proporcionais | aproveitar critérios; rejeitar proibição universal de delegação não solicitada como política da V2 |
| Anthropic: objetividade, delegação proativa, todo muito frequente | aproveitar objetividade; evitar ritual de todo para qualquer pergunta e delegação por mera disponibilidade |
| default: menos de quatro linhas, nenhum comentário, lint/typecheck obrigatório | rejeitar absolutos: podem omitir evidência, impedir comentário útil e gerar carga sem benefício |
| Gemini CLI `Google/gemini-cli.md:23–43` (amostra independente) | localizar e ler estrategicamente; declarar cobertura parcial, não carregar corpus por hábito |
| Codex `OpenAI/Codex/plan_mode.md:19–39` e Claude `agents/Plan.md:10–20` (amostras independentes) | distinguir análise de execução; não importar tags ou permissões proprietárias |
| Mistral Code e GLM README (amostras independentes) | insuficientes para inferir arquitetura de harness ou superioridade de modelo |

Correções ao próprio parecer independente: rejeitada sugestão de confinar todo
arquivo à raiz do repositório; contradiz Tasker generalista e autorização por recurso.
Controle de caminhos/symlinks pertence ao runtime e ao escopo autorizado, não a um
confinamento universal inventado. Teto da máquina fica no contexto operacional,
não hardcoded no kernel portátil.

Conflitos históricos que NÃO foram importados:

- plano:68 e processo:220 ainda citam 3+3; norma atual é 1+1 e memória disponível
  mínima aproximada de 1,2 GB. Demora de cinco minutos é sinal para diagnóstico,
  não prova suficiente de saturação.
- plano:263 manda rollback; processo:802 exige autorização. Não conceder rollback
  automático nem limpeza/morte de processos pela simples entrada de uma fase.
- processo:136 manda revisor executar; D-018 da V2 manda somente inspecionar.
- processo:846 vincula gate ao arquivo editado, mas o próprio método permite
  decisões técnicas rotineiras; gate deve acompanhar a decisão/efeito.
- processo:88 usa 20 linhas como limite de dependência; :96 usa a palavra “e”
  como teste de coesão; :104 impõe soft delete. São heurísticas ou escolhas de
  produto, não invariantes universais de engenharia.
- “tipo garante entrada” não vale em fronteiras não confiáveis. Não importar
  proibição de validação runtime só porque o código possui tipos estáticos.
- plano:113 declara superioridade/custo de modelos sem benchmark local; não
  promover isso a roteamento comprovado. Uma sessão por etapa também é heurística.

A R2 adapta gatilhos e estado do processo, não seus 17 passos ao contexto permanente.
System fino permanece candidato; sua utilidade como bloco separado e a migração
das políticas de ferramentas precisam de experimento. Não há alegação de redução
de tokens ou melhoria de desempenho; a proposta cresceu onde havia lacunas de
comportamento. Próxima avaliação deve medir prompt composto e execução, não só texto.

Fonte local: `prompt-reference`, commit `f475e8b2b11ca7540a37234a451e9f085471bd94`.

A coleção é pública e não oficial. A autenticidade, data de captura, completude e correspondência com produtos reais não foram comprovadas. O conteúdo foi tratado como dado não confiável: nenhuma instrução encontrada nele foi executada, nenhum script foi chamado, nenhuma instalação foi feita e nenhum segredo, pessoal ou export de conversa foi acessado.

O contrato de comparação foi lido antes da pesquisa: `docs/core/CONTRACT.md`, `docs/core/DECISIONS.md`, `AGENTS.md`, `docs/INDEX.md` e `docs/core/BACKLOG.md`. O critério de aceitação aqui é documental: um padrão só pode ser recomendado se não contrariar o contrato. Eficácia de prompt, seleção de agente, permissões, isolamento, composição, ferramentas e comunicação continuam não testadas.

## método e contagens

O inventário foi obtido pela árvore Git do SHA informado, com exclusão de caminhos sob `assets/` e `workflows/`. Foram considerados textuais os arquivos com extensões `md`, `txt`, `xml`, `json`, `jsonc`, `yaml`, `yml` e `skill`.

| estado | quantidade | significado |
| --- | ---: | --- |
| lido aprofundado | 14 | leitura direta, com extração de regras, conflitos e limites; arquivos maiores que a janela foram complementados por seções e buscas focadas |
| triado | 419 | path, README/índice quando aplicável e buscas temáticas corpus-wide; não é leitura integral |
| não lido | 0 | todo arquivo textual entrou na triagem, mas 419 não foram lidos linha a linha |
| textual total | 433 | soma dos estados acima |
| não textual excluído | 55 | árvore restante, incluindo imagens e formatos não classificados como texto |
| caminhos excluídos explicitamente | 1 | item sob `assets/` ou `workflows/` |

A busca temática usou `grep` em todos os Markdown do corpus, em lotes paralelos, para `delegate/subagent/review/verify/validation`, segredos/credenciais, autorização/confirmação/destruição, inspeção/escopo e ferramentas do projeto. Os resultados foram limitados pela ferramenta a 100 ocorrências por consulta quando havia mais; isso serve para triagem, não para contagem de prevalência.

### atualização verificável da leitura integral

O quadro acima é o baseline da primeira rodada. Ele não deve ser interpretado como leitura integral: “triado” continua significando que não há confirmação de EOF. Na rodada posterior, só foram promovidos a “integral” os arquivos cuja leitura em ranges de no máximo 150 linhas foi reportada com EOF explícito.

| grupo sem sobreposição | arquivos com EOF confirmado | linhas reportadas |
| --- | ---: | ---: |
| `Anthropic/` (inclui `claude-design/skills`) | 36 | 6.428 |
| `Google/` | 21 | 3.293 |
| `OpenAI/` (paths individualmente confirmados, incluindo Codex, API e Old) | 37 | 18.634 |
| `README.md`, `xAI/`, `Qwen/`, `Pi/`, `Perplexity/` | 23 | 10.019 |
| `Misc/` | 24 | 5.079 |
| **mínimo documental confirmado** | **141** | **43.453** |

Reconciliação conservadora por quantidade: **433 textuais no inventário; 141 com EOF confirmado; 292 ainda sem confirmação de leitura integral**. O número 141 é o conjunto auditável pelos retornos dos lotes, não uma alegação de que os demais foram lidos. Há arquivos Anthropic e OpenAI ainda explicitamente pendentes; não foram promovidos por nome, `grep` ou `glob`.

### atualização desta rodada

Depois do quadro anterior, foram confirmados com leitura efetiva até EOF: os 6 arquivos root OpenAI que estavam truncados (`gpt-5.4-thinking.md` 1.444 linhas, `gpt-5.3-instant.md` 1.250, `gpt-5.2-thinking.md` 1.284, `gpt-5-thinking.md` 1.175, `gpt-4.5.md` 143 e `chatgpt-gpt-5-agent-mode.md` 1.444); os 34 paths restantes de `OpenAI/Old/**` e `OpenAI/Codex/**` reportados individualmente pelo lote; e novos paths Anthropic, incluindo `claude-mobile-ios.md` (1.812), `claude-science.md` (1.746), `claude-in-chrome.md` (1.218), `raw/claude-sonnet-4.6-raw.md` (1.721), `old/claude-sonnet-4.md` (653), `old/claude-opus-4.5.md` (1.205), além dos `official/**` explicitamente listados no retorno do lote.

Esses retornos elevam o mínimo confirmado para **pelo menos 192 de 433 arquivos**; portanto, **pelo menos 241 ainda não têm confirmação EOF**. Essa é uma contagem mínima conservadora porque os retornos não forneceram uma lista completa sem sobreposição de todos os paths Anthropic já lidos. Não atribuo EOF a arquivos apenas parcialmente mostrados.

Restante explicitamente não fechado ao encerrar esta rodada: `Anthropic/claude-code/**` (skills, commands, output-styles, prompts e archive), parte de `Anthropic/official/**`, `Anthropic/raw/**` e `Anthropic/old/**` (incluindo as variantes `old/claude-4.5-sonnet.md`, `old/claude-4.1-opus-thinking.md`, `old/claude-3.7-sonnet.md`, `old/claude-3.7-sonnet-w-tools.md`, `old/claude-3.7-sonnet-w-tools.xml`, `old/claude-3.7-sonnet-full-system-message-humanreadable.md` e `old/claude-3.7-full-system-message-with-all-tools.md`), além de paths fora de Anthropic/OpenAI que não estão na lista EOF individual desta rodada. Motivo real: a ferramenta de leitura truncou respostas acima de 50 KB e a sessão atingiu o limite operacional antes de concluir a paginação e a enumeração sem sobreposição. Esses paths permanecem pendentes, não lidos.

## lotes de leitura

### lote 0 · contrato e método

Lidos integralmente antes de tocar nos documentos: `AGENTS.md`, `docs/core/CONTRACT.md`, `docs/core/DECISIONS.md`, `docs/INDEX.md` e `docs/core/BACKLOG.md`. Fatos usados: quatro principais sem personalidade/modelo fixado; Leader coordena e revisa sem implementar; revisores só inspecionam e reportam; Tasker cobre sistemas e automação; RTK é padrão forte apenas para comandos compatíveis; docs são fonte da verdade; instrução textual não prova runtime.

### lote 1 · produtos gerais e coordenação

| estado | caminho | linhas | foco |
| --- | --- | ---: | --- |
| lido aprofundado | `Anthropic/claude-cowork/claude-cowork.md` | 2503 | autonomia, tarefas, verificação, pesquisa, arquivos e limites |
| lido aprofundado | `Anthropic/claude-cowork/claude-cowork-dispatch.md` | 695 | roteamento, sessão de tarefa, comunicação e desktop |
| lido aprofundado | `Misc/warp-2.0-agent.md` | 104 | pergunta versus tarefa, terminal, escopo, segurança |
| lido aprofundado | `Perplexity/perplexity-computer.md` | 455 | autonomia, todo, conectores, confirmação, subagentes e entrega |
| lido aprofundado | `Anthropic/claude-design/claude-design.md` | 2621 | fluxo de design, artefatos, validação e edição direcionada |

Para Cowork, Cowork Dispatch e Claude Design, a saída da leitura direta ultrapassou a janela do leitor em alguns pontos. As seções relevantes foram localizadas por `grep` e lidas por faixas. Portanto, “lido aprofundado” não significa transcrição ou auditoria integral de cada linha.

### lote 2 · engenharia, revisão e subagentes

| estado | caminho | linhas | foco |
| --- | --- | ---: | --- |
| lido aprofundado | `Anthropic/claude-code/claude-code-fable-5.1.md` | 6621 | evidência, autonomia, memória, agentes, skills e revisão |
| lido aprofundado | `OpenAI/Codex/codex-full.md` | 11103 | leitura antes de editar, escopo, testes, Git e delegação |
| lido aprofundado | `OpenAI/Codex/codex-auto-review.md` | 107 | revisão, edição mínima, segurança e confirmação |
| lido aprofundado | `Anthropic/claude-code/agents/general-purpose.md` | 21 | agente generalista e ownership |
| lido aprofundado | `Anthropic/claude-code/agents/Explore.md` | 44 | busca somente leitura e proibições de edição |
| lido aprofundado | `Anthropic/claude-code/agents/Plan.md` | 57 | planejamento somente leitura e arquivos críticos |

Nos três prompts longos, foram lidos integralmente os blocos de operação e os trechos apontados por buscas. O restante foi triado por termos e posição; não alego leitura linha a linha completa.

### lote 3 · construção e CLI

| estado | caminho | linhas | foco |
| --- | --- | ---: | --- |
| lido aprofundado | `Google/ai-studio-build.md` | 240 | intenção, implementação, secrets, rede e preview |
| lido aprofundado | `Google/gemini-cli.md` | 254 | contexto, intenção, ciclo pesquisa-estratégia-execução e subagentes |
| lido aprofundado | `OpenCode/opencode.md` | 329 | concisão, leitura do repositório, verificação, lint/typecheck e Git |

### lote 4 · triagem de padrões adicionais

Entraram na triagem, sem leitura integral: todas as demais árvores de `Anthropic/`, `OpenAI/`, `Google/`, `Perplexity/`, `xAI/`, `Microsoft/`, `Cursor/`, `Meta/`, `Misc/`, `Mistral/`, `Kimi/`, `Qwen/`, `Pi/`, `DeepSeek/`, `Notion/`, `GLM/`, `OpenCode/`, `.github/` e o `README.md` raiz.

### lotes posteriores · EOF comprovado e pendências

Nota de cronologia R2: os dois parágrafos seguintes preservam um checkpoint
anterior à seção “atualização desta rodada”. Para os paths expressamente
confirmados nessa atualização, o status parcial abaixo foi superado. Para os
demais, a pendência continua. A reconciliação completa por path permanece aberta;
estes checkpoints não devem ser somados nem tratados como inventário atual único.

Foram confirmados posteriormente, em ranges de até 150 linhas: `Anthropic/claude-design/skills/**` (22 arquivos, 1.183 linhas), `Anthropic/official/README.md`, dois arquivos `official/`, dois `raw/` e `old/default-styles.md`; `Google/` (21 arquivos, 3.293 linhas); `Misc/` (24 arquivos, 5.079 linhas); 23 arquivos de `README.md`, `xAI/`, `Qwen/`, `Pi/` e `Perplexity/` (10.019 linhas); e os 37 paths OpenAI registrados na tabela de atualização (18.634 linhas). Os retornos informaram EOF individual; nenhum conteúdo foi executado.

Permaneceram explicitamente parciais no encerramento desta rodada, entre outros, `Anthropic/old/claude-sonnet-4.md`, `old/claude-opus-4.5.md`, `old/claude-4.5-sonnet.md`, `old/claude-4.1-opus-thinking.md`, `old/claude-3.7-sonnet.md`, variantes `old/*-w-tools*` e arquivos OpenAI como `gpt-5-thinking.md`, `gpt-5.4-thinking.md`, `gpt-5.3-instant.md`, `gpt-5.2-thinking.md`, `gpt-4.5.md`, `Old/o4-mini.md` e `Old/o3.md`. O motivo é a interrupção da sessão após os agentes reportarem os lotes verificáveis; esses arquivos não foram promovidos nem contados como integrais.

O lote integral de `Misc/` reforçou padrões compatíveis com o contrato: inspeção antes de editar, ownership de arquivos, menor patch, preservação de trabalho alheio, validação pós-alteração e confirmação para efeitos destrutivos. Também mostrou conflitos que foram rejeitados como regras globais: idioma e formato de produtos específicos, disciplina de uma ferramenta por passo, exigências de memória, vieses de produto e logging obrigatório. Pesquisa/citações permanecem condicionais ao pedido e à natureza dinâmica da informação; não viram obrigação universal.

Contagens por grupo operacional, sempre com status `triado`: `Anthropic/` 23 arquivos de topo, `Anthropic/claude-code/skills/` 152 no total, `Anthropic/official/` 36, `OpenAI/` 34, `OpenAI/API/` 8, `OpenAI/Codex/` 17, `OpenAI/Codex/old/` 12, `OpenAI/Old/` 15, `Google/` 23, `Perplexity/` 5, `xAI/` 14, `Misc/` 24, `Microsoft/` 5, `Meta/` 3, `Kimi/` 2, `Qwen/` 2, `Mistral/` 2, `Cursor/` 1, `Pi/` 1, `DeepSeek/` 1, `Notion/` 1, `GLM/` 1, `OpenCode/` 1, `.github/` 2 e `README.md` 1. Há sobreposição intencional entre grupos-pai e subárvores; o total sem sobreposição é 433.

## inventário de paths e status

O status abaixo se aplica a cada arquivo textual sob o prefixo indicado. Os 14 caminhos de `lido aprofundado` estão individualizados nas tabelas dos lotes. Todos os demais paths da árvore Git textual estão em `triado`, não em “lido”.

| prefixo/path | estado real | observação |
| --- | --- | --- |
| `README.md` | triado | origem declarada, índice de produtos e aviso de coleção de prompts |
| `.github/CONTRIBUTING.md`, `.github/FUNDING.yml` | triado | metadados/contribuição, não fontes principais |
| `Anthropic/claude-cowork/claude-cowork.md` | lido aprofundado | lote 1 |
| `Anthropic/claude-cowork/claude-cowork-dispatch.md` | lido aprofundado | lote 1 |
| `Anthropic/claude-cowork/setup-cowork/SKILL.md`, `setup-writing-style/SKILL.md` | triado | skills de produto não adotadas |
| `Anthropic/claude-design/claude-design.md` | lido aprofundado | lote 1 |
| `Anthropic/claude-design/skills/**` | triado | 22 skills; nenhum runtime adotado |
| `Anthropic/claude-code/claude-code-*.md` | lido aprofundado apenas `claude-code-fable-5.1.md`; demais triados | variações de produto/modelo |
| `Anthropic/claude-code/agents/general-purpose.md`, `Explore.md`, `Plan.md` | lido aprofundado | lote 2 |
| `Anthropic/claude-code/agents/claude.md`, `claude-code-guide.md`, `statusline-setup.md` | triado | subagentes adicionais |
| `Anthropic/claude-code/skills/**`, `commands/**`, `output-styles/**`, `prompts/**`, `archive/**` | triado | skills, comandos, estilos e material arquivado |
| `Anthropic/official/**`, `Anthropic/raw/**`, `Anthropic/old/**` | triado | capturas/variantes, sem seleção por autenticidade |
| `OpenAI/Codex/codex-full.md` | lido aprofundado | lote 2 |
| `OpenAI/Codex/codex-auto-review.md` | lido aprofundado | revisão Codex |
| `OpenAI/Codex/**` restantes | triado | modos, variantes e prompts antigos |
| `OpenAI/API/**`, `OpenAI/Old/**`, `OpenAI/*.md` | triado | API, ferramentas e variantes |
| `Google/ai-studio-build.md` | lido aprofundado | AI Studio Build |
| `Google/gemini-cli.md` | lido aprofundado | Gemini CLI |
| `Google/*.md` restantes | triado | produtos Google adicionais |
| `OpenCode/opencode.md` | lido aprofundado | OpenCode |
| `Perplexity/perplexity-computer.md` | lido aprofundado | Perplexity Computer |
| `Perplexity/*.md` restantes | triado | produtos Perplexity adicionais |
| `Misc/warp-2.0-agent.md` | lido aprofundado | Warp |
| `Misc/*.md` restantes | triado | ferramentas diversas |
| `Cursor/cursor.md`, `Microsoft/**`, `Meta/**`, `Mistral/**`, `Kimi/**`, `Qwen/**`, `Pi/**`, `DeepSeek/**`, `Notion/**`, `GLM/**`, `xAI/**` | triado | fontes adicionais e variações |

Esse inventário preserva o baseline e os paths exatos dos lotes lidos. A atualização acima é a fonte do estado atual de EOF; paths não listados nela permanecem sem confirmação integral, mesmo quando apareceram na árvore Git ou em buscas temáticas.

## padrões extraídos por papel

### líder/orquestração

Fato observado: Cowork Dispatch separa orquestração de execução e encaminha cada tarefa a uma sessão; Perplexity recomenda subagentes para isolar contexto; Gemini descreve orquestração estratégica; Codex e Claude Code pedem delegação com objetivo e retorno.

Padrão aproveitável: líder recebe objetivo, restrições, ownership e critérios de aceite; delega implementação; recolhe evidência; integra; faz revisão mestre e coordena a verificação. Revisores especializados só inspecionam e reportam.

Rejeição: não importar a regra literal “Leader nunca executa verificações”. O contrato local permite ao Leader inspecionar e executar verificações, mas proíbe implementação/correção. Também não importar dispatch proprietário, nomes de ferramentas, sessões remotas ou exclusividade de equipes sem prova.

### coder

Fato observado: Codex, Claude Code, Gemini CLI e OpenCode repetem “ler antes”, respeitar convenções, editar pequeno, não inventar dependências e validar; AI Studio Build separa pergunta, mudança e ambiguidade.

Padrão aproveitável: reproduzir/limitar, aplicar menor patch, preservar mudanças alheias, testar no menor escopo válido e relatar saída real. Coder cobre software, não operação geral de sistemas.

Rejeição: não importar stacks, portas, frameworks, APIs, estilos de frontend ou modelos fixos de fornecedores. São pressupostos de runtime específicos.

### tasker

Fato observado: Warp distingue pergunta de tarefa e opera no terminal; Perplexity cobre conectores e pesquisa; Cowork prevê arquivos e tarefas desassistidas; prompts de automação insistem em escopo, retorno e não-repetição cega.

Padrão aproveitável: Tasker é generalista operacional para sistemas, redes, CLI, automação, arquivos e integrações autorizadas, não somente Linux. Deve inspecionar estado, escolher a menor operação reversível, respeitar autorização e entregar evidência.

Rejeição: não importar “sempre listar conectores”, caixa persistente, créditos, navegador proprietário, endpoints, portas ou APIs de produto.

### designer

Fato observado: Claude Design explora referências antes de criar, faz edição direcionada, preserva âncoras, exige revisão visual e reduz componentes prematuros; AI Studio e Codex enfatizam acessibilidade e estados reais.

Padrão aproveitável: Designer cobre design/UI/UX, preserva vocabulário visual existente, pergunta somente ambiguidades materiais, cria entregável coerente, verifica legibilidade/acessibilidade e não reescreve o que não foi pedido.

Rejeição: não adotar Design Component, `DCLogic`, `ready_for_verification`, streaming, `hint-size`, regras de CSS ou APIs de artefato como contrato V2. São capacidades não comprovadas e poderiam conflitar com a pilha local.

### revisão/verificação

Fato observado: Claude Code insiste em reportar o que aconteceu; Codex Auto-review prioriza bugs e regressões; Gemini chama validação de caminho da finalização; Warp e OpenCode pedem saída observável.

Padrão aproveitável: revisão é somente leitura e reporta achados; execução de testes fica com principal/Leader conforme o contrato. “Concluído” exige evidência, e falha/skip aparece antes da conclusão.

## rejeições e conflitos

1. **Persona, produto e modelo.** Capturas fixam identidades, personalidades, datas, modelos e URLs. O contrato exige quatro principais sem personalidade/modelo fixado. Rejeitado.
2. **Ferramenta como comportamento.** Nomes como `TaskCreate`, `SendUserMessage`, `start_task`, conectores, MCPs, `ready_for_verification` e APIs de design descrevem superfícies de outros produtos. Não provam existência local. Rejeitado como dependência.
3. **Autonomia versus autorização.** Há fontes que mandam agir sem perguntar e outras que confirmam quase toda mutação. A síntese local mantém autonomia para trabalho pertinente, mas exige autorização específica para destruição, privilégio, publicação, deploy e envio privado, conforme contrato.
4. **Revisor versus executor.** Algumas fontes acoplam revisão e correção, ou mandam o agente lançar subagentes que editam. O contrato local separa revisor somente leitura e principal responsável pela execução. Rejeitado onde houver edição pelo revisor.
5. **Memória e dados pessoais.** Fontes prescrevem memória persistente, conectores e perfis. O contrato prioriza docs do projeto, não herda memória global legada e exclui `pessoal/` e exports. Rejeitado.
6. **Rede, secrets e login.** Fontes variam entre buscar automaticamente, entregar credenciais por canais protegidos e usar conectores. A regra local mais restritiva prevalece: não ler, pedir, guardar, imprimir ou injetar segredos; não acessar pessoal/exports.
7. **Validação declarada versus observada.** Prompts usam “must verify”, mas nenhuma captura demonstra que o runtime executa a validação. Adotado apenas como requisito de processo, não como prova.
8. **Conflitos internos das fontes.** Cowork Dispatch repete blocos de dispatch; Claude Design restringe armazenamento de navegador em um contexto e prescreve `localStorage` em outro contexto de mídia; arquivos exibem catálogos e reminders injetados junto com o prompt. Isso reduz confiança e reforça a classificação como corpus não autenticado.

## importância validada contra o contrato

| conclusão | contrato | eficácia runtime |
| --- | --- | --- |
| leitura antes de editar e escopo mínimo | compatível e útil | não testada |
| Leader coordena, delega implementação e revisa | compatível, com proibição local de implementar/corrigir | não testada |
| revisor só inspeciona e reporta | explicitamente exigido | não testada |
| Tasker generalista operacional | compatível com escopo `systems and automation` | não testada |
| Designer preserva contexto visual e verifica entrega | compatível | não testada |
| RTK prioritário em comandos compatíveis | exigido pelo contrato; corpus não fornece prova local | não testada |
| sem herança, sem memória legada, sem config ativa | exigido por decisões e sessão | confirmado apenas como estado documental desta rodada |
| composição, ordem, seleção, permissões e MCP | pendências explícitas do contrato/backlog | não testada |

## lacunas e próximos testes

Continuam sem prova: composição observável de system/kernel/operate/AGENTS/contexto; ordem de carregamento; ausência de reinjeção; seleção real dos quatro principais; ownership e concorrência de subagentes; permissões e MCP efetivos; RTK sem hook/telemetria; Exa/Sequential Thinking seletivos; comunicação Zed entre sessões; isolamento real; e cenários representativos dos quatro papéis.

Esta pesquisa não executou builds, testes, instalação, launcher ou OpenCode. Não houve mudança de configuração. O próximo passo seguro é transformar a proposta em experimento isolado, com cada componente validado separadamente e sem substituir o legado.
