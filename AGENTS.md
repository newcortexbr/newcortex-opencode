# opencode prefs v2

base para construir e validar uma V2 do OpenCode, preservando o legado.
leia este arquivo, `docs/INDEX.md` e `docs/core/BACKLOG.md` antes de editar;
consulte `DECISIONS.md` e `LOGIC.md` no core conforme o trabalho.

`AGENTS.md` é a instrução canônica; `CLAUDE.md` deve ser um symlink relativo
para ele, nunca uma cópia mantida separadamente.

## documentação viva

- `docs/core/` é a fundação do projeto e fonte da verdade:
  - `BACKLOG.md`: tudo que será feito e foi feito, status, dependências e
    evidências; preserve o histórico e atualize a cada rodada.
  - `DECISIONS.md`: escolhas, perguntas respondidas, resposta aprovada e
    impacto; não registre proposta pendente como decisão.
  - `LOGIC.md`: funcionamento básico de cada componente, seus limites e
    relações; descreva o estado real, distinguindo o planejado.
- `docs/additive/` contém contexto, fontes, investigações e materiais
  temporários, inclusive afazeres auxiliares; não substitui os contratos do
  core nem cria uma fila concorrente ao backlog.
- mantenha `docs/INDEX.md` como mapa dos documentos. registre novas tarefas
  no backlog mesmo quando descobertas em materiais adicionais.
- ao fim de cada rodada, atualize o estado e a evidência no backlog; registre
  decisão material em decisions; atualize logic quando o funcionamento mudar.
- não transforme hipótese em decisão nem marque entrega sem validação.

## operação

- inspecione o estado atual antes de mudar; preserve trabalho de outras
  sessões. diante de conflito entre documentos, esclareça antes de implementar.
- preserve a instalação legado e não acesse credenciais.
- a base local é OpenCode `1.18.30`; launcher, comandos e limites estão em
  `docs/OPENCODE-ISOLATED.md`. isolamento de configuração/estado não é sandbox.
- a configuração viva da V2 é `v2/` (`opencode.json`, `kernel.md`, `agent/*.md`),
  carregada pelo launcher. mudança de comportamento dos agentes acontece ali, não
  por texto avulso; valide com `debug config` e `debug agent <nome>`.
- não habilite herança, migre componentes ou substitua a instalação global
  implicitamente; respeite os bloqueios do backlog e decisões aprovadas.
- aplique o menor patch necessário e valide com saída observável; reporte
  separadamente fatos, hipóteses e pendências. não invente testes ou resultados.
- use `todowrite` para trabalho não trivial e `question` diante de dúvida
  material, risco ou ação privilegiada/destrutiva.
- nunca inclua exports de conversa, credenciais ou estado local em commits.
