# auditoria da base isolada — 2026-09-12

Executado por: audit-sonnet (team opencode-v2-isolation)
Binário: `.opencode-local/bin/opencode` v1.18.30
Launcher: `./opencode-isolated` (env -i, XDG locais, OPENCODE_PURE=1)

---

## 1. verificação de isolamento (antes/depois)

Arquivos globais monitorados antes e após todos os comandos:

| arquivo | mtime antes | mtime depois | alterado? |
|---|---|---|---|
| `~/.config/opencode/opencode.jsonc` | 1788620399 | 1788620399 | não |
| `~/.local/share/opencode/auth.json` | 1789226043 | 1789226343 | **sim** |
| `~/.cache/opencode/models.json` | 1789225741 | 1789225741 | não |
| `~/.local/state/opencode/kv.json` | 1787870231 | 1787870231 | não |

**fato:** o `auth.json` global mudou de timestamp durante a sessão (12:14:03 → 12:19:03).
**causa identificada:** a sessão OpenCode legada global estava ativa concorrentemente
(`~/.local/share/opencode/opencode.db` com mtime 12:20:29, posterior ao início dos meus comandos).
O processo isolado não tem acesso a `~/.local/share/opencode/` (XDG_DATA_HOME apontado para
`.opencode-local/data`). Nenhuma entrada de auth no log isolado. Alteração não causada pelo launcher.

**conclusão do isolamento:** nenhum arquivo global criado ou alterado pelo processo isolado.

---

## 2. subcomandos disponíveis (`--help`)

```
opencode completion
opencode acp                 (ACP server)
opencode mcp                 (manage MCP servers)
opencode [project]           (TUI — não executado)
opencode attach <url>        (não executado)
opencode run [message..]     (não executado — chama provedor)
opencode debug               (ver seção 3)
opencode providers           (aliases: auth)
opencode agent
opencode upgrade             (não executado)
opencode uninstall           (não executado)
opencode serve               (não executado — TUI/headless)
opencode web                 (não executado — TUI/browser)
opencode models [provider]
opencode stats
opencode export [sessionID]
opencode import <file>       (não executado)
opencode github              (não executado)
opencode pr <number>         (não executado)
opencode session
opencode plugin <module>     (não executado)
opencode db                  (não executado)
```

Flags globais relevantes: `--pure`, `--port`, `--hostname`, `--model`, `--agent`, `--auto`,
`--mini`, `--log-level`.

---

## 3. subcomandos de debug (`debug --help`)

```
opencode debug config        show resolved configuration
opencode debug lsp           (não executado)
opencode debug rg            (não executado)
opencode debug file          (não executado)
opencode debug scrap         list all known projects
opencode debug skill         list all available skills
opencode debug snapshot      (não executado)
opencode debug startup       print startup timing
opencode debug agent <name>  show agent configuration details
opencode debug v2            debug v2 catalog and built-in plugins
opencode debug info          show debug information
opencode debug paths         show global paths
opencode debug wait          (não executado — espera indefinida)
```

---

## 4. caminhos resolvidos (`debug paths`)

Todos os caminhos ficam dentro de `.opencode-local/`:

```
home    .opencode-local/home
data    .opencode-local/data/opencode
bin     .opencode-local/cache/opencode/bin
log     .opencode-local/data/opencode/log
repos   .opencode-local/data/opencode/repos
cache   .opencode-local/cache/opencode
config  .opencode-local/config/opencode
state   .opencode-local/state/opencode
tmp     .opencode-local/tmp/opencode
```

**fato:** caminhos são os mesmos independentemente do cwd (por design — XDG fixos no launcher).
O teste de diretório neutro (`/tmp/v2-neutral`) não foi possível executar via mcp_Bash por
restrição de `external_directory` da sessão. Os caminhos são constantes (derivados de `BASE_DIR`
no launcher), então o resultado seria idêntico.

---

## 5. configuração efetiva (`debug config`)

```json
{
  "agent": {},
  "mode": {},
  "plugin": [],
  "command": {},
  "username": "unknown"
}
```

**fato:** configuração completamente vazia — sem agentes customizados, plugins, comandos ou
username configurados. `OPENCODE_DISABLE_PROJECT_CONFIG=1` impede leitura do `opencode.json`
da raiz do projeto.

---

## 6. skills carregadas (`debug skill`)

Apenas uma skill built-in:

```json
[{
  "name": "customize-opencode",
  "description": "Use ONLY when the user is editing or creating opencode's own configuration...",
  "location": "<built-in>"
}]
```

**fato:** `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` suprime scan de `~/.claude/skills/` e
`~/.agents/skills/`. Nenhuma skill externa, nenhuma skill de projeto. Apenas `customize-opencode`
(registrada em código em `packages/core/src/plugin/skill.ts`).

---

## 7. agentes disponíveis (`debug agent <name>` / `agent list`)

7 agentes nativos, sem customização:

| nome | modo | ferramentas habilitadas |
|---|---|---|
| `build` | primary | bash, read, glob, grep, edit, write, task, webfetch, todowrite, websearch, skill, question |
| `plan` | primary | idem a build; edit negado globalmente exceto `.opencode/plans/*.md` |
| `general` | subagent | idem a build; todowrite=false, question=false |
| `explore` | subagent | somente read, glob, grep, bash, webfetch, websearch; edit/write/task/skill=false |
| `compaction` | primary (hidden) | tudo negado exceto internal |
| `summary` | primary (hidden) | tudo negado exceto internal |
| `title` | primary (hidden) | tudo negado exceto internal |

**fato:** os agentes são todos built-in (campo `"native": true`). Nenhum definido via
arquivo `.opencode/agent/` (projeto config desabilitada) nem via `opencode.json` (vazio).

**nota sobre permissão `external_directory`:** todos os agentes pré-autorizam acesso a
`.opencode-local/data/opencode/tool-output/*` e `.opencode-local/tmp/opencode/*`. Fora disso,
`external_directory` é `ask` por padrão.

---

## 8. MCP servers (`mcp list`)

```
▲  No MCP servers configured
```

**fato:** nenhum MCP configurado. `OPENCODE_DISABLE_DEFAULT_PLUGINS=1` e `OPENCODE_PURE=1`
inibem qualquer plugin que pudesse registrar MCPs automaticamente.

---

## 9. providers e credenciais (`providers list`)

```
┌  Credentials /home/dasher/projects/opencode-prefs-v2/.opencode-local/data/opencode/auth.json
│
└  0 credentials
```

**fato:** auth.json isolado existe mas está vazio (sem credenciais). Nenhum provider autenticado.

---

## 10. debug v2 (`debug v2`)

```json
{
  "providers": [],
  "default": { "_id": "Effect", "op": "OnSuccess", ... },
  "small": {}
}
```

**fato:** catálogo v2 sem providers registrados. O campo `default` retorna um objeto interno
Effect (fibra não resolvida) — indica que o modelo padrão não pôde ser determinado sem
credencial/provider. `small` também vazio.

---

## 11. sessões e uso (`session list`, `stats`)

- sessões: 0
- custo total: $0.00
- tokens: 0

**fato:** nenhuma sessão criada no ambiente isolado. DB local criado (`opencode.db` 249 KB)
mas sem dados de sessão — o DB é inicializado vazio no primeiro boot.

---

## 12. informações do sistema (`debug info`)

```
opencode version: 1.18.30
os: Linux 7.3.0-rc2-1-cachyos-rc-vaio-lite x64
terminal: unknown
plugins:
external plugins disabled (--pure)
```

**fato:** `terminal: unknown` é esperado (env -i sem TERM/COLORTERM). Plugins externos
desabilitados confirmado. Nenhum plugin listado.

---

## 13. startup timing (`debug startup`)

```
690.332488 ms
```

---

## 14. estrutura de arquivos em `.opencode-local/`

```
bin/
  opencode      184 MB  (binário oficial 1.18.30)
  n2o             9 MB  (helper nativo)
cache/opencode/
  bin/           (vazio — sem downloads de LSP/binários extras)
config/opencode/
  .gitignore     (63 bytes — gerado automaticamente)
data/opencode/
  log/opencode.log   (5,9 KB — logs das execuções de inspeção)
  opencode.db        (249 KB — DB inicializado vazio)
  opencode.db-shm    (32 KB)
  opencode.db-wal    (259 KB)
  repos/             (vazio)
state/opencode/
  locks/
    5c66e5e3b8983799862ad04525e318ec1105d8ac.lock  (lock de processo)
tmp/
  .bcdddfffbc95b33f-00000000.so  (5,5 MB — módulo nativo temporário, JS FFI/Node.js)
home/           (vazio — HOME isolado)
```

**fato:** `OPENCODE_DISABLE_LSP_DOWNLOAD=1` manteve `cache/opencode/bin/` vazio. Nenhum
download de modelos (`OPENCODE_DISABLE_MODELS_FETCH=1`) — sem `models.json` local.
O `.so` em `tmp/` é um módulo nativo carregado em runtime pelo binário (provavelmente
better-sqlite3 ou similar); é gerado pelo próprio processo e descartável.

---

## 15. log de configuração (extrato do `opencode.log`)

O log confirma o ciclo de carregamento:

```
message=bootstrapping directory=/home/dasher/projects/opencode-prefs-v2
message=loading path=.opencode-local/config/opencode/config.json      → não encontrado
message=loading path=.opencode-local/config/opencode/opencode.json    → não encontrado
message=loading path=.opencode-local/config/opencode/opencode.jsonc   → não encontrado
message="all LSPs are disabled"
message="all formatters are disabled"
message=init
```

**fato:** o binário tenta carregar `config.json`, `opencode.json` e `opencode.jsonc` do
config dir isolado, não os encontra, e inicializa com defaults. LSP e formatters desabilitados
confirmado (sem binários disponíveis e sem config que os habilite).

---

## 16. o que NÃO foi possível observar sem autenticar/TUI

| item | motivo |
|---|---|
| lista de modelos efetiva (`models`) | requer provedor autenticado para resolução |
| modelo padrão resolvido | `debug v2` retorna fibra Effect não resolvida sem provider |
| instruções/system prompt efetivo | só visível em sessão interativa com provedor |
| ferramentas MCP funcionando | nenhum MCP configurado; conexão exigiria rede+provider |
| `debug lsp`, `debug rg`, `debug file` | não executados (comandos de debug de ferramentas, não de estado) |
| `debug snapshot` | não executado (debug de snapshots de sessão, nenhuma sessão existe) |
| teste de diretório neutro `/tmp/v2-neutral` | bloqueado por `external_directory deny` da sessão pai |

---

## 17. síntese

**fato:** a base isolada carrega hoje:
- 1 skill built-in (`customize-opencode`)
- 7 agentes built-in (`build`, `plan`, `general`, `explore`, `compaction`, `summary`, `title`)
- 0 MCPs configurados
- 0 providers/credenciais
- 0 plugins externos
- 0 configuração de usuário (opencode.json local vazio)
- DB e log isolados criados; sem sessões, sem tokens consumidos

**fato:** isolamento confirmado — nenhum arquivo global criado pelo processo isolado; a
alteração em `~/.local/share/opencode/auth.json` é atribuída à sessão legada global ativa
concorrentemente.

**hipótese:** o cwd continua sendo o diretório do projeto (`/home/dasher/projects/opencode-prefs-v2`)
em todas as execuções — comportamento esperado pelo launcher, que não altera o cwd.
