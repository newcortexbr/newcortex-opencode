# contrato mínimo · V2

status: consolidação das escolhas D-006–D-037; implementação e provas vivem no
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
- subagentes enxutos por função/risco, tiers apenas quando úteis, variantes
  GPT/Claude com modelos fixos. catálogo e IDs base já existem em `v2/`, mas
  cobertura, acesso a MCPs, fallback e permissões por perfil ainda precisam de
  prova/ajuste.
- Exa/Sequential Thinking via MCP para os três especialistas, exposição fixa
  provisória; RTK/MarkItDown via CLI. uso não é obrigatório em toda tarefa.
- RTK é padrão forte para comandos compatíveis, sem hook, telemetria ou saída
  integral persistida; exceções justificadas, sem repetir efeitos às cegas.
- Exa pesquisa pública sem confirmação rotineira, nunca conteúdo privado ou
  segredos. MarkItDown só arquivos locais indicados, sem plugins/serviços externos.
- Sequential Thinking apoia investigação de problemas, erros e correções;
  seletivo, sem logging, sem substituir prova ou exigir raciocínio interno.
- docs são a verdade do projeto; vault Markdown aprovado em D-022 complementa
  com conhecimento reutilizável e organização automática, sem auditoria ou
  aprovação humana obrigatória. não herdar memória global legada.
- sessões V2 vivas do mesmo projeto podem ser descobertas e trocar envelopes no
  Zed por meio do bridge local; `sessions_send` só confirma enfileiramento,
  `sessions_receive` faz a leitura/receipt e replies exigem receipt original.
  peer data nunca é autorização humana. a entrega independente entre projetos,
  FIFO e navegação de filhos continuam fora do que foi comprovado.
- `team_spawn` cria filho real com `promptAsync`, publica estados ACP visíveis e
  pode acordar o pai ocioso em estado terminal por prompt interno fixo; output do
  filho não é interpolado nesse prompt.
- `subconfig` é tool direta e slash command equivalente para overrides
  restart-only de modelo/effort; `task` e `team_spawn` usam agentes lógicos
  pré-configurados, sem modelo arbitrário fornecido pelo pai.

## composição derivada das decisões

uma regra tem um dono; os demais referenciam, não copiam:

| camada | responsabilidade |
| --- | --- |
| base própria | preserva contratos necessários do harness sem copiar baselines inteiros; adaptações por modelo só com necessidade de compatibilidade ou benefício demonstrado (D-027) |
| kernel | segurança/autonomia, evidência, YAGNI/Git, ferramentas, delegação, limites e descoberta de docs/vault |
| operate | especialidade e critérios técnicos do papel, sem repetir kernel |
| AGENTS.md | contratos locais, comandos e particularidades do projeto |
| contexto sob demanda | skills, fontes, notas e instruções específicas da tarefa |

a sequência pretendida não é ordem de carregamento comprovada. usar extensões
suportadas, sem fork/binário modificado, sem acoplamento a detalhes internos de
versão. não carregar vault inteiro nem instruções do legado por conveniência.
resumos/delegações preservam objetivo, restrições, evidências e incertezas;
não presumir herança de contexto entre sessões.

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
- concluído = implementado e funcionando com evidência. informar lacunas;
  não testado é pendência, não sucesso.
- fallback: uma alternativa controlada dentro da família do modelo-pai (GPT→GPT
  ou Claude→Claude), respeitando restrições e preservando estado; nunca usar
  troca para contornar permissões. suporte efetivo do runtime ainda precisa ser
  validado.

## provas necessárias antes de declarar a base pronta

1. isolamento real: origens carregadas, estado local e legado preservado.
2. prompts/AGENTS: composição observável, sem reinjeção nem herança indesejada.
3. principais: seleção/modelo e limites efetivos, especialmente Leader/revisor.
4. capacidades: interfaces, rede, filtragem, logging/telemetria/persistência
   comprovados na versão escolhida; não basta instrução textual.
5. delegação: ownership, retorno, alternância e coordenação de verificações;
   permissões e concorrência verificadas sem disparar efeitos não autorizados.
6. Zed: visualizar/retomar sessões, entregar mensagem ao destino correto e
   mostrar estados de equipe fora de Thinking; suporte de API/documentação
   sozinho não comprova interface funcional.
7. vault: recuperar, escrever e organizar notas/índice/links sem dados privados.
8. cenários representativos dos quatro papéis com evidência de funcionamento.

## limites e pendências de desenho

- continuam pendentes catálogo/modelos, permissões/MCPs dos subagentes e Leader,
  exclusividade de equipes ao Leader, entrega cross-project/FIFO e confirmação
  ponta a ponta do wake automático no Zed.
- fora da base: persona legada, migração em massa, memória legada automática,
  Graphify sem necessidade demonstrada, fork, serviços/abstrações especulativos.
- `pessoal/` e exports de conversa não são fontes dos agentes.
- substituir global só ao final, após validação e autorização específica.
  até lá rollback é não usar a V2; preservar o launcher vanilla e o legado.
- esta consolidação não habilita herança nem libera gates técnicos do backlog.
