# documentação

## core

- `core/BACKLOG.md` — fila, histórico e evidências por rodada.
- `core/DECISIONS.md` — decisões respondidas e impacto.
- `core/LOGIC.md` — funcionamento básico e limites reais da V2.
- `core/CONTRACT.md` — contrato mínimo consolidado, limites e provas pendentes.
- `core/VAULT-ARCHITECTURE.md` — desenho aprovado do vault e validação do piloto.

- `PROMPTS.md` — export dos prompts vigentes (kernel, dez agentes, commands) com
  modelo e effort resolvidos; gerado por `scripts/export-prompts.py`.

## additive

Os relatórios `HARNESS-*` da varredura de projetos saíram de `additive/` e vivem
em `vault/agents/projetos/`, fora do versionamento: descrevem sistemas de
terceiros e não são material público. Continuam sendo a entrada para o trabalho
de harness — `HARNESS-COMPARATIVO` para o método e os atritos, `HARNESS-CORPUS`
para cobertura, `HARNESS-PROPOSTA` para o catálogo H01–H28 e `HARNESS-HANDOFF`
para retomada. O que vira decisão aprovada é promovido a `core/`, que é público.

- `additive/PROMPT-READINGS.md` — corpus fixado, lotes de leitura, padrões e cobertura parcial.
- `additive/PROMPT-PROPOSAL.md` — rascunhos originais de system/kernel/operates; não ativos.
- `additive/PLANO_MESTRE.md` e `additive/PROCESSO_INICIO_PROJETO.md` — fontes históricas fornecidas pelo usuário; gatilhos e método avaliados na R2, sem importar políticas antigas automaticamente.

- `additive/CONTEXT-2026-09-10.md` — síntese da conversa anterior e limites.
- `additive/CAPABILITIES-2026-09-10.md` — avaliação documental de Exa, RTK,
  MarkItDown e Sequential Thinking, comandos, matriz e gates propostos.

- `additive/SESSIONS-2026-09-11.md` — pesquisa de sessões, Zed/ACP e limites do Ensemble.
- `additive/INTERSESSION-PROGRESS-2026-09-14.md` — requisitos esclarecidos,
  API intersessão, ponte local ACP, smokes e limite de validação no Zed.
- `additive/VAULT-2026-09-11.md` — proposta de vault obsidian (piloto em `vault/`).

- `additive/INTEGRATION-1.18.30.md` — como a 1.18.30 monta prompt, instruções,
  permissões e subagentes; base técnica da configuração `v2/`.
- `additive/AUDIT-ISOLATED-2026-09-12.md` — auditoria observável da base isolada
  antes da V2 (agentes nativos, skills, MCPs, plugins, credenciais).
- `additive/ROADMAP-V2.md` — etapas, dependências e critérios para completar a
  V2, sem substituir a fila do backlog.
- `additive/AGENT-MATRIX.md` — matriz completa agentes→modelo→variant→tools→MCP→ownership.
- `additive/SESSION-LIMITS.md` — limites attach/sessões independentes e decisão de escopo.
- `additive/CAPABILITIES-LOCAL.md` — instalação e provas locais RTK/MarkItDown, com limites.
- `additive/REVIEW-2026-09-13.md` — revisão independente, regressão repetida e achados R-01–R-06.

## operação

- `OPENCODE-ISOLATED.md` — execução local isolada do OpenCode `1.18.30`.
- `../v2/` — configuração viva da V2: `opencode.json`, `kernel.md` e
  `agent/*.md`. carregada pelo launcher via `OPENCODE_CONFIG_DIR`.
- `../scripts/acp-bridge.py` e `../v2/plugins/session-bridge.mjs` — ponte ACP
  e ferramentas locais de sessões/equipes.
- `../.opencode/command/subconfig.md` e `../v2/subagent-models.json` — comando
  e overrides explícitos de modelo/effort dos subagentes.
