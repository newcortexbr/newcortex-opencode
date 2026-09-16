# integração OpenCode 1.18.30 — pesquisa de código

status: pesquisa somente leitura, tag `v1.18.30`; comprova comportamento do
código consultado, não da instalação local ativa (launcher isolado não executado).
fontes: leitura direta via `raw.githubusercontent.com/anomalyco/opencode/v1.18.30/`.

---

## 1. `agent.prompt` substitui ou complementa o system prompt nativo?

**SUBSTITUI** o baseline por modelo, mas não elimina os demais contextos.

Fonte: `packages/opencode/src/session/llm/request.ts`, função `prepare`, linhas ~57-67:

```ts
const system = [
  [
    ...(input.agent.prompt ? [input.agent.prompt] : SystemPrompt.provider(input.model)),
    ...input.system,
    ...(input.user.system ? [input.user.system] : []),
  ]
    .filter((x) => x)
    .join("\n"),
]
```

Lógica: se `agent.prompt` existe → usa `agent.prompt`; caso contrário → usa
`SystemPrompt.provider(input.model)` (baseline selecionado por modelo).
Os demais blocos (`input.system`, `input.user.system`) são **sempre** incluídos,
independentemente de `agent.prompt` estar ou não presente.

`input.system` vem do caller (veja seção 2). `input.user.system` é o campo
`system` do último `SessionV1.User`, passado via `PromptInput` opcional.

Conclusão confirmada: `agent.prompt` é um **substituto total** do baseline por
modelo. Não é uma adição ao baseline; o baseline não aparece quando `agent.prompt`
está definido. Os demais contextos (ambiente, instruções, MCP, skills) continuam
sendo injetados normalmente.

---

## 2. Montagem completa do system: ordem entre componentes

A montagem final acontece em dois lugares distintos.

### Parte A — `system[]` enviado ao LLM (request.ts, linhas ~57-67)

```
[agent.prompt OU baseline-por-modelo]
+ input.system   (concatenado via "\n")
+ input.user.system
```

Tudo é `join("\n")` em uma única string antes de ir ao array.
Após isso, um hook plugin `experimental.chat.system.transform` pode reescrever.
Para OpenAI OAuth, o resultado vai em `options.instructions`; nos demais
provedores, cada item do array vira uma mensagem `{role: "system"}`.

### Parte B — o que compõe `input.system` (prompt.ts, linhas ~1257-1268)

```ts
const [skills, env, instructions, mcpInstructions, modelMsgs] = yield* Effect.all([
  sys.skills(agent),
  sys.environment(model),
  instruction.system().pipe(Effect.orDie),
  sys.mcp(agent, session.permission),
  MessageV2.toModelMessagesEffect(msgs, model),
])
const system = [
  ...env,
  ...instructions,
  ...(mcpInstructions ? [mcpInstructions] : []),
  ...(skills ? [skills] : []),
]
```

Componentes, na ordem:

| posição | origem | conteúdo |
| --- | --- | --- |
| 1 | `sys.environment(model)` | modelo, cwd, worktree, plataforma, data, referências |
| 2 | `instruction.system()` | AGENTS.md / CLAUDE.md globais + locais + `instructions:` do config |
| 3 | `sys.mcp(agent, ...)` | `<mcp_instructions>` dos servidores MCP permitidos |
| 4 | `sys.skills(agent)` | catálogo de skills disponíveis |

Ordem completa no payload final (concatenada em uma string):

```
[agent.prompt OU baseline-por-modelo]
+ env (modelo, cwd, worktree…)
+ instruções (AGENTS.md, CLAUDE.md, instructions:)
+ MCP instructions
+ skills
+ input.user.system (se houver)
```

---

## 3. `instructions` no opencode.json e descoberta nativa de AGENTS.md

### AGENTS.md é descoberto nativamente

Fonte: `packages/opencode/src/session/instruction.ts`, função `system()` e
`systemPaths()`:

```ts
const globalFiles = [
  path.join(global.config, "AGENTS.md"),
  ...(!flags.disableClaudeCodePrompt ? [path.join(global.home, ".claude", "CLAUDE.md")] : []),
]
const instructionFiles = [
  "AGENTS.md",
  ...(!flags.disableClaudeCodePrompt ? ["CLAUDE.md"] : []),
  "CONTEXT.md", // deprecated
]
```

Comportamento `systemPaths()`:

1. Procura `AGENTS.md` (e `CLAUDE.md`, se não desabilitado) no diretório
   global de config → adiciona o primeiro que existir.
2. Usa `findUp(instructionFile, ctx.directory, ctx.worktree)` para subir de
   `ctx.directory` até `ctx.worktree`, buscando `AGENTS.md`/`CLAUDE.md` →
   adiciona o primeiro match encontrado (não empilha múltiplos).
3. Processa cada entrada de `config.instructions` (campo `instructions:` do
   opencode.json): se for URL `http(s)://` → fetch remoto; se for caminho
   relativo → usa `globUp`; se for absoluto → `glob` direto.
   Todos os resultados entram no conjunto.

`instruction.system()` lê cada path do conjunto e formata:
`Instructions from: <path>\n<conteúdo>`.

### Campo `instructions:` no opencode.json

Fonte: `packages/core/src/v1/config/config.ts`, definição do schema:

```ts
instructions: Schema.optional(Schema.mutable(Schema.Array(Schema.String))).annotate({
  description: "Additional instruction files or patterns to include",
})
```

Aceita array de strings: caminhos relativos (globbed em relação ao worktree),
caminhos absolutos, `~/…` (relativo ao home), ou URLs `https://`. Mergeado com
`concat de arrays` em múltiplos configs (config global + configs de projeto),
sem deduplicação implícita de conteúdo.

Limitação: a descoberta nativa de `AGENTS.md` e o campo `instructions:` são
**dois mecanismos distintos**. Se o AGENTS.md local já está sendo descoberto
via `findUp`, listá-lo também em `instructions:` vai injetá-lo duas vezes.

---

## 4. Permissões efetivas por agente

### Chaves de permissão existentes

Fonte: `packages/opencode/src/agent/agent.ts` (definições dos agentes nativos)
e `packages/opencode/src/permission/index.ts`:

Permissões são `PermissionV1.Rule[]`:
```ts
{ permission: string, pattern: string, action: "allow" | "ask" | "deny" }
```

Ferramentas com aliases especiais no sistema de permissões
(`permission/index.ts`, função `disabled`):

```ts
const edits = ["edit", "write", "apply_patch"]   // mapeados para "edit"
const reads = ["list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource"] // mapeados para "read"
```

Permissões relevantes identificadas nos agentes nativos:

| chave | significado |
| --- | --- |
| `*` | wildcard, abrange tudo |
| `edit` | escrita de arquivos (edit, write, apply_patch) |
| `read` | leitura de MCP resources |
| `bash` | execução de bash/terminal |
| `task` | lançar subagentes |
| `todowrite` | ferramenta todowrite |
| `glob`, `grep`, `list` | busca |
| `webfetch`, `websearch` | rede |
| `external_directory` | acesso a diretórios externos (com subpadrões por glob) |
| `doom_loop` | limite de iterações |
| `question` | ferramenta question |
| `plan_enter`, `plan_exit` | modos de planejamento |
| `skill` | ferramentas de skill |

### `edit: deny` realmente bloqueia escrita via bash?

**NÃO** de forma automática. `edit: deny` bloqueia as ferramentas `edit`,
`write` e `apply_patch` (via o alias `edits[]` em `permission/index.ts`), mas
`bash` é uma ferramenta separada com sua própria chave de permissão.

Para restringir escrita via bash, é necessário também `bash: deny` (ou `"*": deny`
seguido de liberações explícitas). O agente `explore` nativo demonstra esse
padrão: ele nega `*` e permite explicitamente `bash`, `grep`, `glob`, etc.,
mas como `edit`/`write` estão negados via `*`, o bash também **poderia** escrever
se bash for permitido e não houver outro bloqueio.

Evidência do agente `explore` em `agent.ts`:
```ts
explore: {
  permission: Permission.merge(
    defaults,
    Permission.fromConfig({
      "*": "deny",
      grep: "allow",
      glob: "allow",
      list: "allow",
      bash: "allow",
      webfetch: "allow",
      websearch: "allow",
      read: "allow",
      external_directory: readonlyExternalDirectory,
    }),
    user,
  ),
  ...
}
```

O runtime não inspeciona o conteúdo dos comandos bash para verificar se eles
escrevem arquivos; o bloqueio é feito somente no nível da ferramenta.

### Restrição por agente: como funciona

Fonte: `resolveTools` em `request.ts`:

```ts
function resolveTools(input: Pick<PrepareInput, "tools" | "agent" | "permission" | "user">) {
  const disabled = Permission.disabled(
    Object.keys(input.tools),
    Permission.merge(input.agent.permission, input.permission ?? []),
  )
  return Record.filter(input.tools, (_, k) => input.user.tools?.[k] !== false && !disabled.has(k))
}
```

As permissões do agente (`agent.permission`) são mergeadas com as permissões
da sessão (`input.permission`). As regras são uma lista ordenada; `findLast`
determina a regra vencedora. Apenas ferramentas com `action: "deny"` e
`pattern: "*"` são removidas do payload.

Limitação crítica: permissões `ask` não bloqueiam a ferramenta do payload; elas
disparam um prompt ao usuário em runtime. Ferramentas `ask` que o usuário não
responder podem travar a execução.

### Granularidade de bash

O bash como ferramenta é all-or-nothing no nível do agente: permitido ou negado.
Não há granularidade de subcomandos no sistema de permissões nativo.

---

## 5. Herança de modelo e variant em subagentes; como `task` escolhe subagente

### Herança de modelo

Fonte: `packages/opencode/src/tool/task.ts`, trecho de criação de sessão filha
(linhas ~142-147):

```ts
const model = next.model ?? {
  modelID: msg.info.modelID,
  providerID: msg.info.providerID,
}
```

O subagente **herda o modelo da mensagem pai** se não tiver modelo fixado
(`next.model`). A variant do pai é também propagada via:

```ts
variant: next.model ? undefined : variant,
```

(onde `variant = msg.info.variant`, da última mensagem do assistente pai).

Se o agente tiver `model` definido na config, o subagente usa esse modelo e
variant é ignorada (passa `undefined`).

### Como `task` escolhe o subagente

O chamador passa `subagent_type: string` que é o nome do agente. O `TaskTool`
faz:

```ts
const next = yield* agent.get(params.subagent_type)
if (!next) {
  return yield* Effect.fail(new Error(`Unknown agent type: ${params.subagent_type} is not a valid agent type`))
}
```

Não há lógica automática de seleção por função/modelo — o nome deve ser
exato e corresponder a um agente registrado (nativo ou via config).
O agente deve ter `mode: "subagent"` ou `mode: "all"` para ser invocável como
subagente (os agentes `primary` como `build` e `plan` estão disponíveis, mas
podem gerar problemas ao serem usados como subagente).

Profundidade máxima de subagentes: configurável via `subagent_depth` no
opencode.json (padrão: 1, ou seja, subagentes de subagentes são bloqueados por
padrão).

### `experimental.primary_tools`

Fonte: `task.ts`, construção de `childToolDenies`:

```ts
...(cfg.experimental?.primary_tools?.map((permission) => ({
  permission,
  pattern: "*" as const,
  action: "deny" as const,
})) ?? []),
```

Ferramentas listadas em `experimental.primary_tools` são negadas
automaticamente aos subagentes. Mecanismo disponível para restringir ferramentas
exclusivas aos agentes primários.

---

## Resumo das 5 perguntas

| pergunta | resposta confirmada | fonte |
| --- | --- | --- |
| 1. `agent.prompt` substitui ou complementa? | **substitui** o baseline por modelo; os demais contextos (env, instructions, MCP, skills) sempre entram | `request.ts` linhas ~57-67 |
| 2. ordem de montagem | baseline/agent.prompt → env → instructions (AGENTS.md etc.) → MCP → skills → user.system | `request.ts` + `prompt.ts` linhas ~1257-1269 |
| 3. `instructions:` e AGENTS.md | AGENTS.md descoberto nativamente via `findUp`; `instructions:` é campo separado para arquivos/URLs adicionais; não são idênticos | `instruction.ts` |
| 4. permissões: chaves, bash, edit | `edit: deny` bloqueia edit/write/apply_patch mas não bash; bash é ferramenta separada; granularidade all-or-nothing | `permission/index.ts`, `agent.ts` |
| 5. herança de modelo/variant; task | subagente herda modelo+variant do pai se não tiver modelo fixado; escolha por nome exato; profundidade padrão = 1 | `task.ts` |

---

## Riscos de enforcement identificados

### Para Leader (coordenação + verificações)

- **Risco: bash amplo permite escrita indireta.** `edit: deny` não bloqueia
  escrita via `bash`. Para restringir Leader a somente leitura, é necessário
  negar `bash` ou usar `"*": deny` + lista de ferramentas permitidas, como o
  agente `explore` nativo.
- **Risco: `experimental.primary_tools` é opt-in.** Ferramentas de implementação
  só são negadas a subagentes se explicitamente listadas ali. Sem isso, subagentes
  herdam o conjunto completo de ferramentas do pool disponível, filtrado apenas
  pelas permissões do agente.
- **Risco: `task: deny` não está no agente `general` por padrão** no código
  consultado; subagentes do tipo `general` podem lançar outros subagentes se
  `subagent_depth > 1`.

### Para reviewer (somente leitura)

- **O agente `explore` nativo é o modelo de referência** para somente leitura:
  nega `*`, permite `bash` (apenas leitura por convenção), `grep`, `glob`,
  `list`, `read`, `webfetch`. Para garantir somente leitura real, `bash` deveria
  também ser negado ou restrito externamente.
- **Instruções no prompt não são controle de acesso**: declarar "não edite" num
  prompt de revisor não impede a ferramenta de ser chamada; somente a regra de
  permissão com `action: deny` tem efeito real.
- **Skills podem introduzir ferramentas adicionais**: se `skill` não for negado
  no agente revisor, a ferramenta `skill` permite carregar skills que podem ter
  comportamentos mais amplos.

---

## Limites desta pesquisa

- Sem execução do launcher, chamada de modelo ou captura de payload real.
- O mapeamento `env → instructions → MCP → skills` foi verificado em `prompt.ts`
  (arquivo truncado; seção relevante confirmada em arquivo salvo em disco pelo
  tool, linhas 1257–1269).
- `permission.ts` com path `src/permission.ts` retornou 404; encontrado em
  `src/permission/index.ts`. Leitura confirmada.
- `system.ts` inclui mais baselines que a leitura R2 documentou (BEAST, GEMINI,
  GPT, ASTRA, KIMI, META, CODEX, TRINITY além de ANTHROPIC e DEFAULT).
- Não foi verificada a interação entre `session.permission` (passado como
  `input.permission` em `request.ts`) e `agent.permission`; ambos são mergeados
  (`Permission.merge`) antes de `resolveTools`.
- `experimental.primary_tools` e `subagent_depth` são configuráveis mas não
  foram testados localmente.
