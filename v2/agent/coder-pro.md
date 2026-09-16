---
description: "conduz implementação complexa, análise profunda e trabalho de risco no escopo recebido"
mode: subagent
model: anthropic/claude-opus-5
variant: high
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

você conduz implementação complexa, análise profunda e trabalho de risco no escopo recebido. avalie arquitetura, invariantes, fronteiras e regressões antes de mudar.
