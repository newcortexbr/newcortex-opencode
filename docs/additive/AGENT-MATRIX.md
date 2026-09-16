# matriz de agentes · V2

derivada de `v2/agent/*.md`, `v2/opencode.json` e diagnósticos `debug agent`
registrados para a versão `1.18.30`. Descreve a configuração resolvida então
observada; não substitui aceites de fluxo ou isolamento.

> **Atualização 2026-09-16 — catálogo unificado.** Os doze subagentes pareados
> GPT/Claude foram substituídos por **seis papéis com um agente cada**:
> `coder-basic`, `coder-plus`, `coder-pro`, `explorer`, `summarizer` e
> `reviewer`. As permissões por papel são as mesmas dos antigos arquivos `-gpt`,
> conferidas como idênticas às `-claude` fora de modelo/variant. O nome lógico
> do `subconfig` passou a ser o próprio agente. As tabelas abaixo preservam o
> estado anterior como histórico: leia família/variant como registro de então,
> não como configuração vigente. Modelo e effort atuais devem ser lidos em
> `v2/agent/*.md` e `v2/subagent-models.json`.

## resumo

| agente | mode | family | variant | task | shell | edit/write | MCP | principais permissões |
|---|---|---|---|---|---|---|---|---|
| **coder** | primary | — | — | allow | allow\* | implícito | — | bash amplo, git push/PR/merge = ask, delegação livre |
| **tasker** | primary | — | — | allow | allow\* | implícito | — | bash amplo, external_directory `/home/dasher/**` (deny ssh/gnupg/aws/opencode-legacy), delegação livre |
| **designer** | primary | — | — | allow | allow\* | implícito | — | bash amplo, git push/PR/merge = ask, delegação livre |
| **leader** | primary | — | — | allow | deny\* (allowlist) | docs/vault | — | bash deny+allowlist (inspeção/verificação), edit/write docs/vault, delegação livre, skill deny |
| **coder-i-gpt** | subagent | GPT | low | deny | allow\* | allow | — | bash amplo (deny sudo/rm-rf/git push/commit/gh), task deny |
| **coder-i-claude** | subagent | Claude | high | deny | allow\* | allow | — | mesmo bash do coder-i-gpt |
| **coder-ii-gpt** | subagent | GPT | medium | deny | allow\* | allow | — | mesmo bash do coder-i-gpt |
| **coder-ii-claude** | subagent | Claude | medium | deny | allow\* | allow | — | mesmo bash do coder-i-gpt |
| **coder-iii-gpt** | subagent | GPT | high | deny | allow\* | allow | — | mesmo bash do coder-i-gpt |
| **coder-iii-claude** | subagent | Claude | high | deny | allow\* | allow | — | mesmo bash do coder-i-gpt |
| **explorer-gpt** | subagent | GPT | low | deny | deny | deny | — | read/glob/grep/list/todowrite allow; bash/deny; task deny |
| **explorer-claude** | subagent | Claude | high | deny | deny | deny | — | igual explorer-gpt |
| **summarizer-gpt** | subagent | GPT | low | deny | deny | deny | — | igual explorer-gpt |
| **summarizer-claude** | subagent | Claude | high | deny | deny | deny | — | igual explorer-gpt |
| **reviewer-gpt** | subagent | GPT | high | deny | deny | deny | — | read/glob/grep/list allow; bash/edit/write/task/webfetch/todowrite/skill deny |
| **reviewer-claude** | subagent | Claude | high | deny | deny | deny | — | igual reviewer-gpt |

\* `allow` ou `allowlist` herdado do `v2/opencode.json` → top-level `permission.read` com denies de segredos; merge por-agente valida denies.

## detalhes por agente

### principais

| agente | modelo fixo | task | shell | edit/write | delegação | MCPs | ownership |
|---|---|---|---|---|---|---|---|
| coder | não | allow | allow (deny sudo/rm-rf/...) | implícito | allow | Exa + Sequential Thinking | implementação, arquitetura, risco |
| tasker | não | allow | allow (deny sudo/rm-rf/...) | implícito | allow | Exa + Sequential Thinking | sistemas, diagnóstico, automação, Linux central |
| designer | não | allow | allow (deny sudo/rm-rf/...) | implícito | allow | Exa + Sequential Thinking | UI/UX, visual, acessibilidade |
| leader | não | allow | deny + allowlist (inspeção/verificação) | docs/vault | allow | Exa + Sequential Thinking | coordenação, revisão mestre, nunca implementa |

### subagentes — tier único

| agente | família | variante | task | shell | edit/write | leitura bloqueada | MCP |
|---|---|---|---|---|---|---|---|
| explorer-gpt | GPT | low | deny | deny | deny | pessoal, conversa*.json, .env*, auth.json | — |
| explorer-claude | Claude | high | deny | deny | deny | idem | — |
| summarizer-gpt | GPT | low | deny | deny | deny | idem | — |
| summarizer-claude | Claude | high | deny | deny | deny | idem | — |

### subagentes — tiers Coder

| agente | família | variante | task | shell | edit/write | leitura bloqueada | MCP |
|---|---|---|---|---|---|---|---|
| coder-i-gpt | GPT | low | deny | allow\* | allow | pessoal, conversa*.json, .env*, auth.json | — |
| coder-i-claude | Claude | high | deny | allow\* | allow | idem | — |
| coder-ii-gpt | GPT | medium | deny | allow\* | allow | idem | — |
| coder-ii-claude | Claude | medium | deny | allow\* | allow | idem | — |
| coder-iii-gpt | GPT | high | deny | allow\* | allow | idem | — |
| coder-iii-claude | Claude | high | deny | allow\* | allow | idem | — |

`\*` bash com denies: `sudo*`, `rm -rf *`, `git push*`, `git commit*`, `gh *`, `/usr/bin/sudo*`, `/bin/sudo*`, `env sudo*`, `doas*`, `su -*`, `sg *`, `rm -r*`, `rm --recursive*`, `rm -fr*`.

### revisores

| agente | família | variante | task | shell | edit/write | leitura bloqueada | MCP |
|---|---|---|---|---|---|---|---|
| reviewer-gpt | GPT | high | deny | deny | deny | pessoal, conversa*.json, .env*, auth.json | — |
| reviewer-claude | Claude | high | deny | deny | deny | idem | — |

## MCPs

| MCP | tipo | habilitado | escopo |
|---|---|---|---|
| exa | remote | false (D-031) | declarado, desligado; sem chave/OAuth |
| sequential-thinking | local (npx) | true | disponível para principais; logging desativado |

## ownership e exclusividade

| recurso | responsável |
|---|---|
| implementação | coder (delega coder-i/ii/iii) |
| sistemas/diagnóstico | tasker (delega explorer/summarizer) |
| UI/UX | designer (delega explorer/summarizer) |
| coordenação + revisão mestre | leader (delega coder/tasker/designer + reviewer) |
| equipes | **exclusivo ao leader** (D-013); sem enforcement nativo |
| verificação executável | principal responsável (leader ou agente-pai) |
| revisão de diff/branch | reviewer (somente inspeção; não edita, não executa) |

## verificações e cobertura

- O checker foi reportado como `PASS` para 16 agentes e 0 falhas em cenários
  sintéticos de regras resolvidas. A cobertura é parcial: não prova semântica
  integral de globs, normalização de caminhos absolutos, ferramentas de busca,
  shell ou sandbox. regressão central final das correções: 27 testes unitários OK e
  checker com 16 agentes/0 falhas em 2026-09-13, incluindo `gh pr merge` como
  `ask` em Coder/Tasker/Designer; nenhum comando `gh` executado.
- `debug config` registrado confirma 20 chaves de agente (16 custom + 4 nativos
  desabilitados); `agent list` registrado mostra 4 primários, 12 subagentes e 3
  internos (`compaction`/`summary`/`title`).
- `debug agent <nome>` é evidência de mapa de regras resolvido, não de contenção
  de processo: a última regra que casa vence e `tools_false` remove ferramentas
  do payload.

## pendências

- acesso MCP por agente (exclusivo do principal ou herdado? hoje sem restrição
  por agente comprovada).
- exclusividade de equipes ao leader: D-013 registra o desenho, mas não há
  enforcement nativo comprovado; não tratá-la como garantia operacional.
- fallback D-037: se existir, é somente dentro da família do agente-pai (GPT
  para GPT; Claude para Claude). A revisão registrou ausência de suporte nativo
  comprovado para fallback automático; isso não autoriza inferir wrapper externo.
- precedência de config de projeto: fixture central passou (custom-agent carregado,
  build desativado); isso não prova que todo override de projeto seja bloqueado.
- shell bypass: denies de `read` não impedem necessariamente
  `bash: "cat /pessoal/secret.txt"`; é risco documentado, fora da cobertura
  parcial do checker, não uma propriedade resolvida.

## fonte

arquivos em `v2/agent/*.md`, `v2/opencode.json`, `scripts/check-v2.py`, `debug config`/`debug agent <nome>`.
data: 2026-09-13.
