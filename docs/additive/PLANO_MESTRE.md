# Plano Mestre: do primeiro commit ao desenvolvimento perpétuo

**Versão 1.0 · 07/09/2026 · vale para qualquer projeto da casa (Claude Code + Agent Teams + Trello)**

Esta página é o roteiro operacional. O método completo está em `~/.claude/docs/PROCESSO_INICIO_PROJETO.md`; as skills globais carregam cada etapa; os agentes globais executam. Aqui você encontra, em ordem, **o que fazer, o que colar no Claude Code e o que conferir** antes de dizer "próxima".

Como usar: abra o Claude Code na pasta do projeto, cole o prompt da etapa, leia o relatório, confira os itens de "Você confere", e só então avance. Uma sessão por etapa.

---

## 0. Ponto de partida

Você chega aqui com a conceituação pronta: documentos-matrizes (spec funcional, regras de negócio, automações) e layouts de teste (mapa de telas, showcase, branding). Nada de código ainda.

**Onde cada coisa mora no repositório**

| Material | Pasta | Regra |
|---|---|---|
| Specs, regras, PDFs convertidos em .md | `docs/fontes/` | intocável; Claude lê, nunca edita |
| Layouts, prints, branding, showcase, mapa de telas | `docs/referencias/` | direção visual, não spec |
| Documentos gerados pelo processo | `docs/*.md` | fonte da verdade a partir da etapa 03 |

Projeto que já nasceu com `docs/md/` ou `docs/mapa-telas/`: não mova nada. Diga ao Claude onde estão as fontes no prompt de discovery.

**Ferramentas instaladas (conferir uma vez)**

| Item | Onde | Verificação |
|---|---|---|
| Claude Code 2.1+ | terminal | `claude --version` |
| MCP Trello, Playwright, Whimsical | `~/.claude.json` | `/mcp` mostra os três conectados |
| Agentes globais (6) | `~/.claude/agents/` | `/agents` lista backend, frontend, senior, qa, security, final |
| Skills globais (10) | `~/.claude/skills/` | digitar `/` mostra `projeto-bootstrap … proxima-etapa` |
| Norma global | `~/.claude/CLAUDE.md` | seções "PROCESSO DE INÍCIO" e "TRELLO" presentes |
| Board Trello do projeto | Trello | colunas REGRAS, A FAZER, FEITOS, ETAPAS, TO-DO, RECURSOS |

---

## 1. O mapa em uma tela

| # | Etapa | Você cola | Quem decide | Trello | Termina quando |
|---|---|---|---|---|---|
| 00 | Bootstrap | `/projeto-bootstrap <nome>` | Claude | – | primeiro commit com `docs/` e `.gitignore` |
| 01 | Input | (você copia as fontes) | Você | – | `docs/fontes/` completo |
| 02–03 | Discovery + docs iniciais | `/discovery` | Claude | – | 7 docs gerados, pendências listadas |
| 04 | Pendências | `/pendencias` | **Você** (gate) | – | DECISIONS.md sem PENDENTE bloqueante |
| 05–06 | Arquitetura + consolidação | `/arquitetura` | **Você** (gate) | – | `STATUS: APROVADA` no ARCHITECTURE.md |
| 07 | CLAUDE.md do projeto | `/project-claude-md` | Claude | linha `Trello:` | comandos verificados |
| 08 | Backlog | `/backlog` | Claude | cria ETAPAS | BACKLOG.md com ownership e dependências |
| 17 | Transição | `/proxima-etapa E-1` | Claude | cria ondas em A FAZER | ondas gravadas, máquina limpa |
| 09–12 | Implementação + verificação | `/epic E-1 onda 1` | Claude Lead | marca checklist, move onda | zero Critical/High |
| 13 | Release candidate | `/release-candidate` | Claude | – | `READY FOR DEPLOY` |
| 14 | Aprovação | "autorizo o deploy" | **Você** (gate) | – | – |
| 15 | Deploy + smoke | prompt da seção 5.3 | Claude | – | smoke verde em produção |
| 16 | Docs finais | `/docs-finais` | Claude | – | RUNBOOK e CHANGELOG atualizados |
| ↻ | Próxima etapa | `/proxima-etapa E-2` | Claude | – | ciclo recomeça |

Só três gates humanos: **04, 05 e 14**. Todo o resto flui sem você.

---

## 2. Dez regras que valem sempre

1. **Nunca acelere pulando entendimento; acelere paralelizando execução.** Código só depois de `APROVADA` no ARCHITECTURE.md.
2. **`docs/` é a fonte da verdade. Trello é o espelho.** Divergiram? Corrige-se o Trello.
3. **Uma etapa por sessão.** Termine com `/proxima-etapa`; abra sessão nova para a próxima.
4. **Todo prompt para subagente é fechado:** ID, objetivo, AC com texto, `own`, docs, comandos permitidos, formato de retorno. O Lead escreve; você nunca fala com subagente.
5. **Ownership antes de paralelismo.** Duas tasks na mesma onda nunca tocam o mesmo arquivo.
6. **Teto da máquina:** 3 typechecks e 3 builds no total, `free -h` antes de rodada pesada, abaixo de 3 GB livres espera-se. Subagente não roda typecheck nem build.
7. **KISS, YAGNI, sem comentário explicativo, sem código morto, tipos nas bordas, idempotência.** Está na seção 3 do processo; o Lead lê antes de implementar.
8. **Revisor procura o catálogo de falhas de IA** (seção 4): invenção, simplificação silenciosa, excesso, inconsistência, segurança, estado, ambiente, relato otimista.
9. **"Concluído" exige comando e saída no relatório.** Sem `TESTS RUN` com contagem, não está concluído.
10. **Decisão de negócio é sua e fica em DECISIONS.md.** Decisão técnica rotineira é do Lead e também fica lá.

---

## 3. Claude Code: o que usar em cada momento

Recursos nativos que sustentam o processo. Tudo abaixo existe na versão 2.1.263; nada aqui é plugin de terceiro.

| Recurso | Para quê | Quando no processo |
|---|---|---|
| **Hierarquia de CLAUDE.md** (`~/.claude/CLAUDE.md` → `./CLAUDE.md` → `./CLAUDE.local.md`) | global = como trabalhamos; projeto = o que o sistema é; local = URLs e dados de teste seus, fora do git | 07 cria o do projeto |
| **`@caminho`** dentro do CLAUDE.md ou no prompt | importa um doc sem colar | qualquer prompt que cite `docs/` |
| **`.claude/rules/*.md`** com `paths:` | regra que só carrega ao tocar certos arquivos (ex.: regras de migrations) | 07, quando o CLAUDE.md passar de 80 linhas |
| **Skills** (`/nome`, `~/.claude/skills/`) | procedimento de etapa carregado no contexto do Lead | todas as etapas |
| **Subagentes** (`~/.claude/agents/`, campo `model`) | contexto novo, ownership fechado, modelo por papel | 09–12 |
| **Agent Teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, já ligado) | lista de tarefas compartilhada, teammates em paralelo, mensagens entre eles | ondas com 3 a 5 tasks |
| **Plan mode** (`Shift+Tab` até "plan") | Claude só lê e propõe; não edita | 02–05 se quiser blindagem extra |
| **`/effort`** (low … max) | esforço do Lead | high na fundação e revisões, medium em ondas rotineiras |
| **`/model`** | trocar modelo do Lead | Fable no Lead; nunca troque os subagentes por aqui, o modelo deles vem do arquivo do agente |
| **`/compact [foco]`** | resume a conversa mantendo o CLAUDE.md | entre ondas longas |
| **`/clear`** | conversa nova | entre etapas |
| **`/rewind`** ou `Esc Esc` | volta código e conversa a um checkpoint | onda que saiu errada; arquivos alterados por shell voltam via git |
| **`/resume`, `claude -c`** | retomar sessão anterior | continuar uma etapa no dia seguinte |
| **`/handoff <foco>`** (skill) | documento de passagem para sessão nova | fim de sessão com contexto relevante |
| **`/context`** | quanto do contexto está ocupado e por quê | quando o Lead começar a "esquecer" |
| **`/memory`** e memória automática (`~/.claude/projects/<slug>/memory/`) | o que não está no repo e precisa sobreviver entre sessões | `/proxima-etapa` grava |
| **`/mcp`** | estado do Trello, Playwright, Whimsical | início de sessão se algo falhar |
| **`/agents`, `/hooks`, `/permissions`, `/status`, `/doctor`** | inspeção de configuração | quando algo não se comporta como este plano diz |
| **`/code-review [nível]`** e **`/verify`** | revisão nativa do diff e verificação do fluxo alterado | complemento ao final-reviewer em tasks isoladas |
| **`!comando`** | roda shell na sessão e a saída entra na conversa | `! free -h`, `! git status` |
| **`Ctrl+B`** / `--bg` | manda comando ou agente para segundo plano | suíte longa enquanto o Lead segue |
| **`Ctrl+O`** | ver o transcript com saída completa das ferramentas | auditar o que um subagente realmente rodou |
| **Worktree** (`isolation: worktree` em agente, `EnterWorktree`) | cópia isolada do repo para experimento ou refactor arriscado | tasks `complexidade: alta` que tocam muita coisa |
| **`/loop`**, `CronCreate` | rodar um prompt em intervalo ou horário | vigiar CI/deploy, regressão noturna |
| **`claude -p "<prompt>" --output-format json`** | modo headless para scripts e CI | smoke test agendado, geração de relatório |
| **Hooks** (`PreToolUse`, `Stop`, `SubagentStop`, `PreCompact` …) | bloquear ou automatizar ações | ex.: proibir `pkill -f` e `prisma migrate reset`; salvar handoff em `PreCompact` |
| **MCP Trello** | ETAPAS, A FAZER, FEITOS, TO-DO | `/backlog`, `/proxima-etapa`, `/epic` |
| **MCP Playwright** | validar tela real, não código | frontend-engineer, qa-engineer, ajustes visuais |
| **MCP Whimsical** | fluxograma, sequência, wireframe a partir do FLOWS.md | 03 e 05 quando um desenho ajuda a aprovar |
| **Skills do repositório** (`.agents/skills/`: accessibility, web-quality-audit, ui-ux-pro-max) | auditoria de interface | antes de entregar tela implementada |

Duas dicas de custo: subagente Sonnet com prompt fechado custa uma fração do Lead e entrega igual; revisor Opus low acha o que Sonnet não acha. Não inverta.

---

## 4. Fase A: fundação (uma vez por projeto)

### 00 · Bootstrap

**Repositório novo:**

```text
/projeto-bootstrap <nome-do-projeto>
```

**Repositório que já existe com documentação (caso deste projeto):**

```text
Este repositório já tem documentação em docs/. Aplique a etapa 00 do processo global sem mover nada:
crie .gitignore, .env.example, README.md e um CLAUDE.md provisório dizendo que o projeto está em discovery,
que a fonte da verdade é docs/ e que não se implementa código até ARCHITECTURE.md estar APROVADA.
As fontes estão em docs/md/ e as referências visuais em docs/mapa-telas/, docs/showcase/, docs/branding/ e docs/referencias/.
Commit: "chore: prepara repositório para o processo de início de projeto".
```

**Você confere:** `git log` mostra o commit; `.env*` está no `.gitignore`.

### 01 · Input (você, sem prompt)

- Specs em `.md` sempre que existir a versão `.md` (PDF só como apoio).
- Layouts, prints e branding em `docs/referencias/` ou nas pastas que já existem.
- Anotações soltas, áudios transcritos, decisões de reunião: um arquivo `docs/fontes/ANOTACOES.md`.
- Commit: `docs: adiciona fontes do projeto`.

### 02–03 · Discovery e documentação inicial

```text
/discovery
As fontes estão em docs/md/ (spec principal: NEW_CORTEX_AREA_CLIENTE_MASTER_SPEC_v2_0.md) e as referências visuais em docs/mapa-telas/ e docs/showcase/.
```

O Claude lê tudo sem programar e gera PRODUCT, REQUIREMENTS, FLOWS, DATA-MODEL, ARCHITECTURE (proposta), ACCEPTANCE e DECISIONS.

**Você confere:** o resumo separa FATO, INFERÊNCIA e PENDENTE; toda contradição entre fontes cita as duas; nenhum RF sem fonte. Leia REQUIREMENTS.md e DECISIONS.md inteiros. É a leitura mais rentável do projeto.

### 04 · Pendências · GATE

```text
/pendencias
```

O Claude apresenta apenas decisões de negócio, uma por vez, com opções, impacto e recomendação. Decisões técnicas rotineiras ele toma sozinho e registra.

**Como responder:** escolha a letra ou escreva a sua versão. Se não sabe, diga "adie: não bloqueia o MVP" e ela fica registrada como pendência não bloqueante.

**Você confere:** DECISIONS.md tem data e autor em cada decisão; REQUIREMENTS/FLOWS/DATA-MODEL foram atualizados.

### 05–06 · Arquitetura · GATE

```text
/arquitetura
```

Leia nesta ordem: ARQUITETURA RECOMENDADA, RISCOS, TRADE-OFFS, DECISÕES QUE PRECISAM DE VOCÊ. Cada tecnologia tem um motivo e uma alternativa descartada. Se algo não tem requisito que o justifique, mande tirar.

**Para aprovar, escreva literalmente:**

```text
Arquitetura aprovada. Consolide a documentação.
```

**Você confere:** cabeçalho `STATUS: APROVADA em <data>`; `grep -n PENDENTE docs/*.md` retorna só pendências não bloqueantes.

### 07 · CLAUDE.md do projeto

```text
/project-claude-md
O board Trello deste projeto é "<nome do board>". Inclua a linha Trello com o ID.
```

**Você confere:** no máximo ~80 linhas; todo comando listado foi executado uma vez; linha `Trello: <id> (<nome>)` presente; `.env.example` espelha as variáveis.

### 08 · Backlog

```text
/backlog
```

Gera BACKLOG.md com epics `[E-X]`, tasks `E-X-Txxx`, `own`, `depende`, `complexidade`, `paralelismo`, grafo de dependências. Cria no Trello um cartão por etapa em ETAPAS com a checklist de tasks.

**Você confere:** fundação (schema, auth, RBAC, contratos, layout base) vem antes de tudo; tasks de dinheiro, concorrência, integração e webhook estão com `complexidade: alta`; ETAPAS no Trello bate com o BACKLOG.md. Se quiser mudar prioridade, é aqui que se muda, no BACKLOG.md.

---

## 5. Fase B: o ciclo de cada etapa (para sempre)

A partir daqui o projeto vive em ciclos. Cada ciclo é uma etapa `[E-X]`. O ciclo tem quatro comandos e dois gates opcionais.

### 5.1 · Abrir a etapa

```text
/proxima-etapa E-1
```

O Claude: mata processos órfãos, apaga builds e caches, registra memória e decisões, marca o BACKLOG.md, calcula as **ondas** (tasks que rodam em paralelo por subagentes diferentes) e cria em A FAZER um cartão por onda, na ordem.

**Você confere:** tabela de ondas faz sentido (fundação primeiro; nada de dinheiro na onda 1 sem schema pronto); A FAZER no Trello mostra as ondas em ordem; `df -h` e `free -h` no relatório. Quer mudar a ordem? Reordene em A FAZER e diga "siga a ordem do Trello".

### 5.2 · Executar as ondas

```text
/epic E-1 onda 1
```

O Lead dispara os subagentes da onda no mesmo turno com prompts fechados, roda typecheck e suíte uma vez, distribui, depois QA + security + final review em paralelo, roteia findings aos donos, regressão, até zero Critical/High. No fim: checklist do cartão `[E-1]` marcada, cartão da onda movido para FEITOS, findings abertos viram `[TD-X]`.

Depois, simplesmente:

```text
agora faça a onda 2
```

ou, se preferir tudo de uma vez:

```text
/epic E-1
```

**Você confere no relatório:** IMPLEMENTADO por task com AC; COMANDOS E RESULTADOS com contagens; FINDINGS; PENDÊNCIAS; TRELLO; PRÓXIMO COMANDO. Relatório sem comando executado não conta.

**Quando o contexto pesar** (relatórios longos, muitas ondas): termine a onda, rode `/proxima-etapa` ou `/handoff` e abra sessão nova. Não empilhe três ondas numa sessão.

### 5.3 · Fechar a release (quando a etapa entrega algo publicável)

```text
/release-candidate
```

Espere `READY FOR DEPLOY`. Se `NOT READY`, o relatório lista o que falta; peça "corrija e rode de novo".

**GATE 14, você:**

```text
Autorizo o deploy em produção desta release.
```

**Deploy (etapa 15):**

```text
Faça o deploy conforme RUNBOOK.md (ou ARCHITECTURE.md se ainda não houver runbook). Depois execute smoke test em produção:
login por perfil, fluxo principal, uma escrita real, logs sem erro, health checks. Reporte cada comando e resultado.
Se qualquer item falhar, faça rollback pelo procedimento documentado e reporte antes de tentar de novo.
```

**Docs finais (etapa 16):**

```text
/docs-finais
```

### 5.4 · Reiniciar

```text
/proxima-etapa E-2
```

E o ciclo recomeça. "Agora faça a etapa 2" é exatamente isto: `/proxima-etapa E-2` seguido de `/epic E-2 onda 1`.

---

## 6. Trello: o board do projeto

O board tem seis colunas. A coluna **REGRAS** prevalece sobre qualquer texto aqui; o Claude a lê antes de escrever.

| Coluna | O que é | Quem mexe |
|---|---|---|
| REGRAS | as normas do board | você |
| ETAPAS | um cartão por etapa `[E-X] título // módulo`, descrição vazia, uma checklist com todas as tasks | `/backlog` cria, `/epic` marca |
| A FAZER | fila ordenada de **ondas** `[E-X] Onda N · resumo // módulo`, tasks na descrição, sem checklist | `/proxima-etapa` cria e ordena; você reordena se quiser |
| FEITOS | ondas concluídas, para sua revisão e arquivamento manual | `/epic` move; só você arquiva |
| TO-DO | listas soltas `[TD-X] título // dd/mm`, descrição começa `[dd/mm // hh:mm]`, uma checklist | Claude (findings) e você (pedidos) |
| RECURSOS | links e acessos | ninguém além de você |

**O que você faz no Trello:** cria `[TD-X]` para pedidos fora do backlog; reordena A FAZER quando muda prioridade; arquiva FEITOS quando revisar. Um `[TD-X]` novo entra no ciclo com:

```text
Leia o cartão [TD-3] no Trello, transforme cada item em task no BACKLOG.md (com own, AC e complexidade) e inclua na próxima onda disponível. Não implemente ainda.
```

---

## 7. Prompts de bolso

**Bug em produção ou em dev**

```text
Bug: <o que acontece> · esperado: <o que deveria> · como reproduzir: <passos>.
Investigue a causa raiz antes de mudar código. Corrija com um teste que falhava antes.
QA do fluxo afetado e dos vizinhos com Playwright. Sem deploy.
```

**Ajuste visual pequeno**

```text
Ajuste visual em <tela>: <o que muda>. Siga docs/mapa-telas/DIRECAO-VISUAL.md e as regras de acessibilidade.
Valide a tela real com Playwright em desktop e mobile antes de reportar.
```

**Mudança de regra de negócio**

```text
Nova regra de negócio: <regra>. Registre em DECISIONS.md com data, propague para REQUIREMENTS, FLOWS,
DATA-MODEL e ACCEPTANCE, e gere as tasks no BACKLOG.md. Não implemente ainda.
```

**Hotfix em produção**

```text
Hotfix: <problema>. Correção mínima, teste que falhava antes, /release-candidate reduzido ao fluxo afetado.
Aguarde minha autorização antes do deploy.
```

**Onde estamos?**

```text
Resuma em 15 linhas: etapa atual, ondas feitas e pendentes (BACKLOG.md e Trello), findings abertos,
últimos comandos de verificação e resultado, próximos três passos.
```

**Trocar de sessão sem perder o fio**

```text
/handoff continuar a etapa E-2 a partir da onda 3
```

---

## 8. Higiene de sessão e de máquina

- **Sessão nova por etapa.** Contexto longo degrada julgamento; `/proxima-etapa` foi feita para ser o último comando de uma sessão.
- **`/compact` quando o relatório de uma onda ficar atrás de muito ruído; `/clear` só entre etapas.**
- **Esforço:** Lead em `high` na fundação (02–08) e nas revisões; `medium` em ondas rotineiras. Subagentes já têm modelo e esforço fixos.
- **Máquina:** antes de qualquer rodada pesada, `free -h`. Typecheck passando de 5 minutos é máquina saturada, não motivo para reexecutar. Nunca `pkill -f`.
- **Limpeza:** `/proxima-etapa` apaga só o regenerável. `node_modules`, bancos locais, `.env*` e `docs/` nunca são tocados.
- **Memória:** o que não está no repo (falha de agente, limite de máquina, decisão de rota) vai para a memória automática na transição. Se o Claude "esqueceu" algo entre sessões, o lugar de gravar é `/proxima-etapa`, não o chat.

---

## 9. Sinais de alerta

| Sintoma | Ação |
|---|---|
| Código antes de `APROVADA` | pare; volte a `/arquitetura` |
| Subagente perguntando decisão técnica rotineira | prompt aberto; peça ao Lead prompt fechado |
| Dois agentes no mesmo arquivo | `own` errado; `/backlog` na epic |
| "Concluído" sem comando e saída | não está concluído; exija verificação |
| Typecheck ou build > 5 min | máquina saturada; contar processos e `free -h` |
| Finding "resolvido" sem reteste | regressão obrigatória |
| Trello divergindo do BACKLOG.md | `/proxima-etapa` de novo |
| Docs descrevendo o que o código não faz | `/docs-finais` |
