# contrato mínimo · V2

status: consolidação das escolhas D-006–D-043; implementação e provas vivem no
backlog.
decisões prevalecem; pendências e evidências vivem em `BACKLOG.md`.

## escopo aprovado

- quatro principais na v1: `Leader`, `Coder`, `Tasker`, `Designer`, selecionados
  pelo mecanismo nativo, sem personalidade e sem modelo fixado.
- `Coder`: software; `Tasker`: generalista operacional (Linux central, não
  exclusivo; pesquisa, diagnóstico, ferramentas e automação); `Designer`: design/UI/UX.
- `Leader`: coordenação e revisão mestre; pode inspecionar e executar
  verificações, nunca implementar nem corrigir a solução. Pode escrever plano,
  backlog, evidências/status, registrar decisões aprovadas e sincronizar o
  acompanhamento autorizado; alteração de requisitos continua delegada.
  Proposta não equivale a aprovação. Revisão delegada só inspeciona
  e reporta. verificações executáveis passam pelo principal responsável.
  Verificações do Leader podem gerar build, cache, cobertura e relatórios locais
  regeneráveis, sem autofix, atualização de snapshots de referência ou alteração
  de dados/serviços compartilhados. Efeitos sensíveis exigem isolamento comprovado
  ou autorização específica, sem dispensar outros gates aplicáveis (D-026).
- subagentes enxutos por função/risco, **um agente por papel** desde D-040:
  `coder-basic`, `coder-plus`, `coder-pro`, `explorer`, `summarizer`, `reviewer`.
  os pares `-gpt`/`-claude` não existem mais; cada troca de modelo é explícita
  via `subconfig` e exige restart. cobertura, acesso a MCPs e permissões por
  perfil ainda precisam de prova/ajuste.
- Sequential Thinking via MCP, habilitado; RTK/MarkItDown via CLI. uso não é
  obrigatório em toda tarefa. Exa permanece declarado e **desligado**, e por isso
  saiu do kernel: instrução sobre ferramenta ausente é ruído de contexto.
- RTK é padrão forte para comandos compatíveis, sem hook, telemetria ou saída
  integral persistida; exceções justificadas, sem repetir efeitos às cegas.
- pesquisa web cobre conteúdo público sem confirmação rotineira, nunca conteúdo
  privado ou segredos. MarkItDown só arquivos locais indicados, sem
  plugins/serviços externos.
- Sequential Thinking apoia investigação de problemas, erros e correções;
  seletivo, sem logging, sem substituir prova ou exigir raciocínio interno.
- docs são a verdade do projeto; vault Markdown aprovado em D-022 complementa
  com conhecimento reutilizável e organização automática, sem auditoria ou
  aprovação humana obrigatória. não herdar memória global legada.
- sessões V2 vivas do mesmo projeto podem ser descobertas e trocar envelopes por
  meio do bridge local; `sessions_send` só confirma enfileiramento,
  `sessions_receive` faz a leitura/receipt e replies exigem receipt original.
  peer data nunca é autorização humana. a entrega independente entre projetos,
  FIFO e navegação de filhos continuam fora do que foi comprovado.
- `team_spawn` cria filho real com `promptAsync` e publica estados de ciclo de
  vida monotônicos (`starting < busy < idle`, `error` uma vez). o wake automático
  do pai ocioso vive no proxy ACP, congelado por D-041, e não tem equivalente TUI.
- **alvo de cliente é o TUI** (D-041). a integração ACP/Zed está congelada: o
  código permanece no repositório e não recebe evolução nem serve de critério de
  aceite.
- `subconfig` é tool direta e slash command equivalente para overrides
  restart-only de modelo/effort; `task` e `team_spawn` usam agentes lógicos
  pré-configurados, sem modelo arbitrário fornecido pelo pai.

## composição derivada das decisões

uma regra tem um dono; os demais referenciam, não copiam:

| camada | responsabilidade |
| --- | --- |
| system fino | linha comum a todos os papéis; é o topo do system prompt efetivo, não preâmbulo decorativo |
| operate | especialidade e critérios técnicos do papel, sem repetir kernel |
| kernel | segurança/autonomia, evidência, ferramentas, delegação, limites e continuidade; agnóstico ao projeto |
| AGENTS.md | contratos locais, vault, comandos e particularidades do projeto |
| contexto sob demanda | skills, fontes, notas e instruções específicas da tarefa |

`system fino` + `operate` formam o `agent.prompt`; `kernel` e `AGENTS.md` entram
como `instructions`. São composições **separadas**, não uma pilha única — confundi-las
foi a causa de uma remoção equivocada em 2026-09-16, registrada no backlog.

Esta instalação **substitui** o system prompt que o OpenCode usaria: em
`packages/opencode/src/session/llm/request.ts` da tag `v1.18.30`, o código escolhe
`agent.prompt` OU `SystemPrompt.provider(model)`. Limite declarado: isso vem de
leitura de código, não de inspeção do payload enviado ao modelo — prova local
ainda pendente no backlog.

Usar extensões suportadas, sem fork/binário modificado (D-011), sem acoplamento a
detalhes internos de versão. Não carregar vault inteiro nem instruções do legado
por conveniência. Resumos/delegações preservam objetivo, restrições, evidências e
incertezas; não presumir herança de contexto entre sessões.

`scripts/export-prompts.py` publica o conjunto vigente em `docs/PROMPTS.md` a
partir da configuração **resolvida pelo launcher**, não do texto dos arquivos.

## operação e conclusão

- autonomia local pertinente à tarefa; destrutivo, privilégio, publicação e
  envio privado exigem autorização específica. nunca acessar segredos.
- reutilizar existente/nativo; dependência local só por necessidade concreta,
  sem abstrações ou extensões especulativas.
- política futura permite commit local validado; push/PR/merge exigem pedido.
  contratos superiores da sessão continuam prevalecendo. commit não é entrega.
- validação na unidade escolhida pelo projeto, no menor escopo tecnicamente
  válido; respeitar onde executar, risco e limites compartilhados da máquina.
  coordenar verificações pesadas, não duplicar execução; parcial não prova todo.
- conclusão se refere a afirmação, alvo, camada e ambiente, nunca a exit code
  (D-042). o limite do agente é **entregue**: efeito demonstrado, com evidência,
  ambiente e limites declarados. **fechado é do usuário**. não há cobrança de
  validação a cada passo, e a ausência dela não é bloqueio. informar lacunas;
  não testado é pendência, não sucesso.
- nenhum estágio anterior passa por posterior: existir não é ser chamado, passar
  não é estar correto, subir não é estar integrado.
- fallback: D-037 previa alternativa dentro da família do modelo-pai, mas ficou
  **inaplicável na prática** com D-040 — sem par por família, não há alternância
  automática. toda troca é explícita via `subconfig`, com restart.

## provas necessárias antes de declarar a base pronta

1. isolamento real: origens carregadas, estado local e legado preservado.
2. prompts/AGENTS: composição observável, sem reinjeção nem herança indesejada.
3. principais: seleção/modelo e limites efetivos, especialmente Leader/revisor.
4. capacidades: interfaces, rede, filtragem, logging/telemetria/persistência
   comprovados na versão escolhida; não basta instrução textual.
5. delegação: ownership, retorno, alternância e coordenação de verificações;
   permissões e concorrência verificadas sem disparar efeitos não autorizados.
6. ~~Zed~~: retirado das provas exigidas por D-041, que congelou a integração
   ACP/Zed e fixou o TUI como alvo. o que segue valendo é a entrega da mensagem
   ao destino correto no bridge local, independente de cliente.
7. vault: recuperar, escrever e organizar notas/índice/links sem dados privados.
8. cenários representativos dos quatro papéis com evidência de funcionamento.
9. D-042 provada por comportamento: os três cenários sanitizados de confusão de
   camada, detectados e nomeados pelo agente sem aviso prévio.
10. D-043 provada por comportamento: a poda de contexto preserva as saídas que
    sustentam a conclusão, inclusive no caso adversário.

## limites e pendências de desenho

- continuam pendentes catálogo/modelos, permissões/MCPs dos subagentes e Leader,
  exclusividade de equipes ao Leader e entrega cross-project/FIFO. o wake
  automático segue sem prova ponta a ponta e, por D-041, deixou de ser meta.
- contexto é recurso governado: o DCP (D-043) poda saídas de ferramenta, e a
  lista de proteção de `v2/dcp.jsonc` existe para que a poda não remova a
  evidência que D-042 exige. as duas decisões são acopladas de propósito.
- fora da base: persona legada, migração em massa, memória legada automática,
  Graphify sem necessidade demonstrada, fork, serviços/abstrações especulativos.
- `pessoal/` e exports de conversa não são fontes dos agentes.
- substituir global só ao final, após validação e autorização específica.
  até lá rollback é não usar a V2; preservar o launcher vanilla e o legado.
- esta consolidação não habilita herança nem libera gates técnicos do backlog.
