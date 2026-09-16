# logic · opencode prefs v2

## objetivo

construir uma configuração V2 mínima, auditável e incremental do OpenCode, sem
alterar a instalação legado durante a investigação.

## documentos

1. `BACKLOG.md` é a fila e o histórico operacional: cada rodada atualiza o
   estado, a evidência e as dependências.
2. `DECISIONS.md` registra somente escolhas respondidas, seu contexto e efeito.
3. `LOGIC.md` descreve o funcionamento observado, o planejado e os limites;
   mudanças de funcionamento atualizam este arquivo na mesma rodada.
4. `docs/additive/` recebe fontes e contexto não canônico; conteúdo útil e
   estabilizado é promovido para `core` em forma compacta.

## construção da V2

1. iniciar por execução isolada e verificar observavelmente o que é carregado;
2. definir o contrato mínimo antes de introduzir qualquer componente;
3. classificar o legado; somente componentes necessários e comprovados podem
   ser selecionados;
4. incluir um componente por vez, validar seu efeito e registrar evidência;
5. manter o legado disponível como rollback por não uso, sem cópia de estado
   nem credenciais.

## memória

uma memória é funcional apenas se a escrita autorizada, a consolidação e a
recuperação forem verificadas. uma permissão declarada ou um documento de
arquitetura não são prova de funcionamento.

## configuração V2 ativa e limites observados

O launcher local usa `env -i`, mantém estado em `.opencode-local/` e aponta
`OPENCODE_CONFIG_DIR` para `v2/`. A configuração viva é
`v2/opencode.json`, com kernel absoluto em
`/home/dasher/projects/opencode-prefs-v2/v2/kernel.md` e agentes em
`v2/agent/*.md`. `debug config` e `debug agent` registrados em 2026-09-12
confirmaram o carregamento da V2 e suas permissões resolvidas.

Para que a descoberta nativa de `AGENTS.md`/`CLAUDE.md` funcione,
`OPENCODE_DISABLE_PROJECT_CONFIG` não é definido pelo launcher. Como efeito,
`opencode.json` e `.opencode/` do projeto aberto também podem mesclar e
sobrepor agentes ou permissões da V2. O isolamento de diretórios e ambiente
não impede essa mescla, não é sandbox de processo e não bloqueia por si só
rede, shell ou scripts do projeto.

Os MCPs declarados são uma seleção fixa da configuração atual: `exa` permanece
declarado e desligado; `sequential-thinking` está declarado como MCP local e
habilitado, com logging de pensamento desativado. Isso não prova carregamento
dinâmico sob demanda, restrição por agente nem uso funcional em uma tarefa.

Os plugins carregados são três: `op-anthropic-auth@0.1.4` (OAuth Anthropic,
D-035), `@tarquinen/opencode-dcp@3.1.15` (poda de contexto, D-043) e o local
`./plugins/session-bridge.mjs`. Os dois externos são resolvidos em
`.opencode-local/cache/opencode/packages/`, com versão fixada — nunca instalação
global e nunca faixa aberta de versão.

O checker local cobre parte do mapa resolvido de permissões e a precedência da
configuração de projeto em fixture. Ele não prova semântica completa de globs,
normalização de caminhos absolutos, ferramentas de busca, bloqueio de shell ou
sandbox; os riscos devem continuar explícitos até aceites correspondentes.

## composição de prompts · aplicada em 2026-09-16

D-025–D-027 definem uma base própria com contratos necessários do harness,
sem cópia integral de baselines. Leader coordena e pode escrever documentação
de coordenação, mas delega implementação/correção e alteração de requisitos.
Suas verificações podem produzir artefatos locais regeneráveis nos limites de
D-026; revisores permanecem sem escrita ou execução de verificações.

A composição deixou de ser apenas roteiro em `additive/PROMPT-PROPOSAL.md`. Hoje
o que está ativo é:

- `agent.prompt` de cada papel = `system fino` + `operate`. A linha `resolva o
  pedido no papel selecionado, usando as capacidades disponíveis no ambiente.`
  abre os dez agentes e **é a camada `system fino`**, não repetição. Como
  `request.ts` da `v1.18.30` escolhe `agent.prompt` OU
  `SystemPrompt.provider(model)`, havendo prompt de agente o baseline do provedor
  não entra: essa linha é o topo do system prompt efetivo.
- `instructions` = `v2/kernel.md`, resolvido por caminho absoluto, mais o
  `AGENTS.md` descoberto nativamente. É uma composição separada do prompt de
  agente.

O kernel ficou agnóstico ao projeto: as regras de vault e de escrita indireta
migraram para `AGENTS.md`, e a menção ao Exa saiu porque a ferramenta está
desligada. Entraram três regras da varredura — verificar vigência antes de
tratar conflito como pergunta aberta; delegação não transfere autorização nem
comprova capacidade; o que se repete vira teste ou procedimento. O §6 passou a
definir conclusão por afirmação/alvo/camada/ambiente e a distinguir **entregue**
(agente, com evidência) de **fechado** (usuário), por D-042.

`explorer` e `summarizer` têm contrato de saída derivado de falhas reais desta
V2: inventário não é leitura, EOF não garante ausência de truncagem, faixa
relatada precisa caber no total, cobertura declarada precisa ser a real.

Limite a não esquecer: a substituição do system prompt vem de **leitura de
código**, não de inspeção do payload. `docs/PROMPTS.md` declara esse limite em
vez de afirmar cobertura, e a prova local continua aberta no backlog.

## catálogo de agentes

Desde 2026-09-16 (D-040) há **um agente por papel**: quatro principais (`coder`,
`tasker`, `designer`, `leader`) e seis subagentes (`coder-basic`, `coder-plus`,
`coder-pro`, `explorer`, `summarizer`, `reviewer`). Os pares `-gpt`/`-claude`
deixaram de existir, então o nome lógico usado pelo `subconfig` é o próprio nome
do agente e cada troca de modelo afeta um único alvo. `AGENT_TARGETS` continua
existindo para listar papéis no índice, agora com um alvo cada.

Consequência a não esquecer: sem par por família, não há alternância automática
GPT↔Claude. A escolha de modelo é sempre explícita e exige restart.

## exposição de ferramentas

A exceção temporária D-039 foi aplicada e depois removida em 2026-09-16:
durante a varredura, `explorer-gpt` teve allow de `external_directory` restrito a
seis projetos; hoje `debug agent` mostra novamente apenas `ask` e os caminhos
internos de tool-output. O episódio registrou um limite real: autorização do
usuário ao principal não concede alcance ao subagente, e a leitura externa
delegada exige permissão explícita mais restart. `debug agent` reflete o
frontmatter resolvido quando o plugin não carrega. A divergência observada antes
— `variant: low` apesar do override medium salvo — tinha como causa o módulo
`v2/plugins/session-bridge.mjs` falhando na avaliação por um token solto na
primeira linha; sem o módulo, nenhuma tool do bridge é registrada e nenhum
override é aplicado. O token foi removido e a linha 1 hoje é o import correto.
Depois da correção e do reinício, `subconfig reload` respondeu normalmente e
`debug agent` passou a refletir o override (`anthropic/claude-sonnet-4-6`,
`medium`). Portanto o diagnóstico só confirma modelo/effort quando o plugin está
carregado — regra geral: **um plugin que não carrega falha em silêncio**, e a
configuração resolvida continua parecendo plausível.

A seleção ativa é a lista fixa declarada na configuração, não um carregador por
necessidade. A escolha de exposição dinâmica continua uma investigação aberta.
Mesmo uma ferramenta declarada/habilitada exige prova separada de descoberta,
permissões e comportamento real.

## intersessão e equipe · implementação local

O plugin `v2/plugins/session-bridge.mjs` é carregado somente quando o launcher
define `OPENCODE_V2_BRIDGE_DIR`; ele não cria ferramentas no OpenCode global.
Sessões vivas são registradas por processo, e a sessão atual pode confirmar seu
metadata com `session.get` quando uma ferramenta é usada. `sessions_list` não
converte o histórico retornado por `session.list` em sessões conectadas.

`sessions_send` grava um envelope atômico em `inbox/<target>` e um evento sem
payload em `events/<target>`. A origem vem de `context.sessionID`; o destino
precisa estar no registry vivo. `sessions_receive` move o envelope para
`receipts`, e reply duplicado é impedido por reserva exclusiva. Peer text é dado
não confiável, não mensagem de usuário e não autorização.

O progresso de ciclo de vida do filho é **monotônico**: `starting < busy < idle`,
com `error` permitido uma vez. Sem isso, `session.status` oscilando busy/idle e
`session.updated` reinjetando `starting` passavam pelo dedup de estado imediato e
geravam uma mensagem por passo do subagente — o flood observado em 2026-09-16.

`team_spawn` é uma tool local mínima baseada em `session.create` +
`session.promptAsync`, não o Ensemble original.

### camada ACP · congelada (D-041)

No modo `acp`, `opencode-isolated` inicia `scripts/acp-bridge.py`, que mantém
requests/responses ACP e consome eventos. Mail e progresso de `team_spawn` são
exibidos como `agent_message_chunk`, fora do bloco recolhido de Thinking, porque
o Zed recolhe thought chunks. O wake automático do pai ocioso vive em
`_inject_internal_prompt`, dentro do proxy, e **não tem equivalente no TUI**.

Desde D-041 o alvo é o TUI e esta camada está congelada: o código permanece, não
recebe evolução e não serve de critério de aceite. Consequência prática a não
esquecer: o único consumidor de `events/` é o `EventStore` do proxy —
`cleanupRegistrations` limpa apenas `registrations/` e `views/`. Fora do ACP,
esse diretório não é drenado.

`/subconfig` é um command de projeto. `subconfig reload` cria um índice local de
providers/modelos; a forma explícita
`/subconfig <agente> <provider/model> <effort>` grava somente overrides em
`v2/subagent-models.json`. No próximo boot, o hook `config` aplica o override.
Desde D-040 cada nome lógico tem **um alvo único**, então não há mais propagação
a pares GPT/Claude. `task` e `team_spawn` escolhem agentes pré-configurados; não
há roteamento automático, troca em filhos já ativos ou modelo arbitrário
informado pelo agente-pai.
O agente atual também pode chamar `subconfig` diretamente; `/subconfig` é apenas
outra forma de invocar a mesma tool. O kernel orienta esse uso e exige informar
o restart.

O status operacional de `team_spawn` sai pelo canal ACP
`agent_message_chunk`, não por `agent_thought_chunk`: o Zed recolhe thought
chunks dentro de “Thinking”, enquanto o status de equipe deve permanecer visível
fora desse bloco. O texto continua prefixado com `[team]` e sanitizado. As
transições `starting/busy`, `idle` e `error` também carregam texto para que a
ponte possa exibir início, conclusão e falha.
Em `idle/error`, se o pai está ocioso, a ponte dispara um prompt interno fixo;
se o pai ainda está ocupado, posterga o wake até o fim do turno. Nenhum payload
do filho é injetado como instrução.

## poda de contexto · DCP

`@tarquinen/opencode-dcp@3.1.15` (D-043) governa o custo de contexto por três
mecanismos independentes:

1. **`compress`** — tool exposta ao agente, que escolhe quando e o quê colapsar,
   substituindo a faixa por um sumário que ele mesmo escreve.
2. **`deduplication`** — mesma tool com os mesmos argumentos: mantém a saída mais
   recente e poda as anteriores.
3. **`purgeErrors`** — poda o input de chamadas que erraram, após N turnos.

O histórico da sessão não é alterado; a poda incide sobre o que é enviado ao
modelo. A configuração vive em `v2/dcp.jsonc`, lido via `$OPENCODE_CONFIG_DIR`.

Ela foi escrita a partir de uma tensão real com D-042: os defaults do plugin
protegem `task/skill/todowrite/todoread`, mas deixam `read`, `grep` e `bash`
desprotegidos — exatamente as ferramentas que produzem evidência. Por isso a
instalação estende `protectedTools` com read/grep/glob/list/bash/webfetch, liga
`turnProtection` (4 turnos), desliga `autoUpdate` (mantém a versão auditada e
zera a única saída de rede do pacote) e mantém `allowSubAgents: false`.

Estado de prova: a substituição por sumário e a lista de proteção foram
exercitadas em sessão real. A poda automática (`deduplication`, `purgeErrors`) e
o caso adversário **não** foram demonstrados; o aceite segue parcial no backlog.

## catálogo de modelos

O launcher não define `OPENCODE_DISABLE_MODELS_FETCH`. Assim, `models --refresh`
 pode atualizar o catálogo público; a execução de 2026-09-15 listou 38 IDs,
 incluindo Muse, Nemotron, Luna, Terra, Sol, Astra, Opus e Sonnet, mas não
 `Inkling`. Catálogo, acesso autenticado e favoritos/configuração do Zed são
 camadas distintas; uma não prova as outras.
