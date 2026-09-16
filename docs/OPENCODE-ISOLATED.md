# OpenCode isolado

Este diretorio contem o binario oficial `1.18.30` para uso local, sem alterar a
instalacao global ou o `PATH`.

## Execucao

Na raiz do diretorio:

```sh
./opencode-isolated --version
```

De qualquer diretorio, use o caminho absoluto do lancador:

```sh
/home/dasher/projects/opencode-prefs-v2/opencode-isolated --help
```

O lancador cria estado somente em `.opencode-local/` e usa `env -i` com os
caminhos XDG locais. Configuracao, dados, cache, estado, temporarios e auth
futuros nao compartilham os diretorios legados.

Desde 2026-09-12 o `OPENCODE_CONFIG_DIR` aponta para `v2/`, que e a
configuracao versionada da V2 (`v2/opencode.json`, `v2/kernel.md`,
`v2/agent/*.md`). Dados, cache e estado continuam em `.opencode-local/`.
Tres plugins sao carregados pela V2, todos resolvidos localmente em
`.opencode-local/cache/opencode/packages/` e nunca instalados globalmente:

- `op-anthropic-auth@0.1.4` — OAuth Anthropic (experimental, D-035);
- `@tarquinen/opencode-dcp@3.1.15` — poda de contexto, configurada em
  `v2/dcp.jsonc` (D-043); expoe a tool `compress` e o command `/dcp-compress`;
- `./plugins/session-bridge.mjs` — local, expoe `sessions_list`,
  `sessions_send`, `sessions_receive`, `team_spawn` e `subconfig`, com estado em
  `.opencode-local/state/session-bridge/`.

Essas ferramentas funcionam na TUI: nenhuma delas depende do ACP. `subconfig` e
uma tool chamavel diretamente pelo agente; `.opencode/command/subconfig.md` e
apenas outra forma de invoca-la. Ela grava overrides em
`v2/subagent-models.json` e so passa a valer apos reinicio.

Texto de outra sessao entra no contexto somente via `sessions_receive`.

A camada ACP esta **congelada** desde 2026-09-16 (D-041): `scripts/acp-bridge.py`
e o ramo `acp` do launcher continuam no repositorio e nao foram removidos, mas
o alvo ativo e a TUI. Ver `core/LOGIC.md` para o que deixaria de existir numa
remocao futura.

## Piloto

```sh
cd /home/dasher/projects/opencode-prefs-v2
./opencode-isolated providers login     # alias: auth
./opencode-isolated models | head
./opencode-isolated                     # TUI da V2
```

Para o experimento Anthropic, com o plugin fixado `op-anthropic-auth@0.1.4`
carregado no cache isolado, execute `providers login`, selecione Anthropic e a
opcao Claude Pro/Max/OAuth apresentada pelo plugin; conclua o navegador. A
credencial resultante fica em `.opencode-local/data/opencode/auth.json`. Nao
cole API key nesse fluxo se a meta for OAuth. O plugin e comunitario e a
Anthropic pode restringir o uso de tokens de assinatura em clientes terceiros.

Na TUI, troque de agente com `Tab` (ou `/agent`) entre `coder`, `leader`,
`tasker` e `designer`; o padrao e `coder`. Subagentes sao alcancados por
delegacao (`task`), com nomes exatos: `explorer`, `summarizer`, `reviewer`,
`coder-basic`, `coder-plus` e `coder-pro`. Desde 2026-09-16 ha um agente por
papel: os pares `-gpt`/`-claude` foram removidos e o nome do papel e tambem o
nome usado no `subconfig`. As mencoes a esses pares abaixo sao historicas.

Piloto validado em 2026-09-12: `coder` com `openai/gpt-5.6-luna` delegou a
`explorer-gpt` e recebeu `DELEGADO=4`. O mesmo OAuth OpenAI rejeita
`gpt-5.4-mini`; os tiers leves GPT foram alinhados ao Luna low. Anthropic está
registrado apenas como API e não participa enquanto a credencial não for válida.
Também foi validada a cadeia `leader`/Luna → `reviewer-gpt`/Astra: o reviewer
confirmou uma seção existente do backlog sem editar nem executar comandos.
O OAuth Codex também rejeitou `gpt-5.4`; o `coder-ii-gpt` usa Luna medium.
OAuth Anthropic foi confirmado em 2026-09-12: Haiku respondeu
`AUTH_ANTHROPIC_OK`, e a cadeia Sonnet → `explorer-claude`/Haiku retornou
`DELEGADO_CLAUDE=sim`.

Para inspecionar os prompts efetivamente resolvidos, use
`python3 scripts/export-prompts.py`, que regenera `docs/PROMPTS.md` a partir de
`debug agent` — nao do texto dos arquivos.

## Uso no Zed (congelado, D-041)

Esta secao e historica. A V2 e operada pela TUI; a configuracao abaixo continua
funcionando, mas nao e mais o caminho validado.

Registre um agente ACP customizado em `~/.config/zed/settings.json`, dentro de
`agent_servers`, sem mexer nas entradas existentes:

```json
"opencode-v2": {
  "type": "custom",
  "command": "/home/dasher/projects/opencode-prefs-v2/opencode-isolated",
  "args": ["acp"],
  "env": {}
}
```

O launcher usa `env -i`, portanto o ambiente do Zed nao e herdado e o
isolamento continua valido. O `cwd` do processo e o projeto aberto no Zed.
A entrada `opencode` de tipo `registry` continua apontando para a instalacao
legado e nao e afetada.

## Alcance e limites

O isolamento fixa os mecanismos existentes na `v1.18.30`: `XDG_*`,
`OPENCODE_CONFIG_DIR`, `OPENCODE_DISABLE_CLAUDE_CODE`,
`OPENCODE_DISABLE_EXTERNAL_SKILLS`, `OPENCODE_DISABLE_DEFAULT_PLUGINS` e
`OPENCODE_PURE`. `OPENCODE_DISABLE_MODELS_FETCH` não é definido: o catálogo
público de modelos pode ser atualizado pelo OpenCode. O ambiente do processo
filho é zerado, portanto credenciais e overrides do shell não são herdados.

`OPENCODE_DISABLE_PROJECT_CONFIG` foi REMOVIDO em 2026-09-12: esse flag tambem
desligava a descoberta nativa de `AGENTS.md`/`CLAUDE.md`, exigida pela V2. Em
troca, `opencode.json` e `.opencode/` do projeto aberto passam a mesclar com a
config da V2 e podem sobrepor permissoes e agentes. Ao abrir um projeto de
terceiros, confira esses arquivos antes.

A versao ainda inclui skills internas do proprio produto e pode acessar a rede
quando uma operacao explicitamente solicitar isso. O lancador nao fornece
credencial, nao chama provedor e nao altera arquivos globais. O diretorio de
trabalho continua sendo o cwd escolhido pelo usuario.

As decisoes acima correspondem ao codigo oficial da tag `v1.18.30`:

- `packages/core/src/global.ts`
- `packages/core/src/flag/flag.ts`
- `packages/opencode/src/config/config.ts`
- `packages/opencode/src/session/instruction.ts`
- `packages/opencode/src/skill/index.ts`

## Verificacao observavel

```sh
./opencode-isolated --version
find .opencode-local -maxdepth 3 -type d -print | sort
find .opencode-local -maxdepth 3 -type f -printf '%P\n' | sort
```

Somente o binario local e os diretorios sob `.opencode-local/` devem aparecer;
o comando `--version` nao inicia autenticacao nem um provedor. Para demonstrar
que a chamada funciona fora da raiz, execute o caminho absoluto acima a partir
de outro cwd.

## Autenticacao futura

Nenhuma autenticacao e configurada automaticamente. Apos uma decisao manual,
use somente o fluxo oficial da CLI `1.18.30` atraves deste lancador e confirme
que o estado resultante esta em `.opencode-local/`. Nao copie `auth.json`, nao
exporte credenciais legadas e nao reintroduza variaveis no ambiente sem uma
revisao explicita do isolamento.

## Rollback

Para voltar ao fluxo legado, pare de chamar este lancador e use a instalacao
global normalmente. A remocao de `opencode-isolated`, `.opencode-local/` e do
pacote baixado e uma acao manual opcional; nada global precisa ser revertido.
