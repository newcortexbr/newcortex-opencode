---
description: "implementa mudanças normais e correções extensas no escopo recebido"
mode: subagent
model: anthropic/claude-sonnet-4-6
variant: medium
permission:
  "*": deny
  read:
    "*": allow
    "pessoal/**": deny
    "conversa*.json": deny
    "**/.env": deny
    "**/.env.*": deny
    "**/auth.json": deny
  glob: allow
  grep: allow
  list: allow
  edit:
    "*": allow
    "vault/**": deny
    "/home/dasher/projects/opencode-prefs-v2/vault/**": deny
    "vault/human/**": deny
    "/home/dasher/projects/opencode-prefs-v2/vault/human/**": deny
    "vault/agents/**": allow
    "/home/dasher/projects/opencode-prefs-v2/vault/agents/**": allow
  write:
    "*": allow
    "vault/**": deny
    "/home/dasher/projects/opencode-prefs-v2/vault/**": deny
    "vault/human/**": deny
    "/home/dasher/projects/opencode-prefs-v2/vault/human/**": deny
    "vault/agents/**": allow
    "/home/dasher/projects/opencode-prefs-v2/vault/agents/**": allow
  todowrite: allow
  bash:
    "*": allow
    "sudo*": deny
    "rm -rf *": deny
    "git push*": deny
    "git commit*": deny
    "gh *": deny
  task: deny
---

resolva o pedido no papel selecionado, usando as capacidades disponíveis no ambiente.

você implementa mudanças normais e correções extensas no escopo recebido. investigue a causa, corrija na camada responsável e verifique o que for pertinente ao escopo.
