# roadmap da V2

plano operacional. o `BACKLOG.md` continua sendo a fila canônica; esta página
organiza as etapas e seus critérios de saída. itens não marcados como feitos
continuam sendo plano, não evidência.

## etapa 1 · fechar catálogo e contratos executáveis

- congelar `Leader`, `Coder`, `Tasker` e `Designer` como principais funcionais;
- fechar Explorer, Summarizer, Coder I/II/III e Reviewer, com pares GPT/Claude
  somente onde a diferenciação for útil;
- definir ownership, permissões, acesso MCP e se equipes ficam exclusivas ao
  Leader; manter revisores read-only e verificações coordenadas;
- aplicar fallback somente na família do modelo-pai (D-037), sem inventar
  fallback se o runtime não o oferecer.

saída: matriz agente→modelo→variant→tools→MCP→ownership aprovada e refletida
em `v2/`; `debug config`/`debug agent` confirmam o enforcement.

## etapa 2 · completar integração do runtime

- provar ordem/composição do system, kernel, operate, AGENTS e contexto;
- validar precedência de `opencode.json`/`.opencode/` do projeto-alvo;
- testar limites do Leader, reviewer, shell e coordenação de verificações;
- verificar fila global de typecheck/build e regras específicas do projeto sem
  disparar concorrência indevida;
- validar fallback GPT→GPT e Claude→Claude em falha controlada.

saída: probes e sessões registradas, sem segredos, com limites observáveis e
nenhuma violação crítica/alta aberta.

## etapa 3 · capacidades selecionadas

- manter Sequential Thinking conectado e testar uso seletivo em investigação;
- instalar/testar RTK localmente, sem hook, persistência integral ou telemetria;
- instalar/testar MarkItDown como CLI local para arquivos indicados, sem plugins
  e sem URLs;
- manter Exa desligado até necessidade explícita; não instalar por simetria;
- medir perda de evidência, custo, latência e comportamento de erro.

saída: cada capacidade tem prova, política de dados, rollback e decisão de
manter/ajustar/descartar; nenhuma ferramenta passa a ser obrigatória por agente.

## etapa 4 · piloto representativo

- executar tarefas pequenas reais nos quatro principais;
- delegar exploração, resumo, implementação e revisão em escopos separados;
- validar revisão de diff/branch, verificação pelo principal e evidência de
  concluído;
- comparar execução direta, subagente e equipe quando aplicável.

saída: matriz cenário→agente→delegação→verificação→resultado, com qualidade,
falhas e custo observados.

## etapa 5 · vault e continuidade

- testar recuperação, escrita, organização automática, índice e links do vault;
- garantir que notas pessoais, exports e credenciais permaneçam fora do corpus;
- decidir o que é conhecimento reutilizável e o que continua apenas no projeto.

saída: piloto do vault válido ou escopo reduzido, sem importar conteúdo pessoal.

## etapa 6 · sessões, equipes e Zed

- validar ACP/Zed para listar, abrir e retomar sessões do mesmo projeto;
- investigar visibilidade de filhos/equipes e mensagens entre sessões
  independentes, sem gate humano de comunicação;
- adotar solução existente somente se preservar isolamento e manutenção
  aceitável; não criar gateway/fork por conveniência.

saída: fluxo funcional demonstrado no Zed ou limitação explícita aceita como
fora da V2 inicial.

## etapa 7 · inventário e migração seletiva

- classificar legado como necessário, quebrado, abandonado ou incerto;
- migrar somente capacidades comprovadas, uma por vez, com rollback;
- não migrar personas, memória automática, Graphify ou integrações sem prova de
  finalidade e funcionamento.

saída: inventário rastreável, componentes escolhidos e nenhuma herança acidental.

## etapa 8 · release e substituição global

- rodar release candidate: segurança, testes, docs, rollback e uso no Zed;
- versionar/commit­ar somente após validação e revisão do usuário;
- preparar launcher/atalho de substituição e preservar o legado como rollback;
- substituir o comando oficial somente após autorização específica do usuário.

saída: checklist `READY FOR CUTOVER`, instruções de reversão e decisão explícita
de troca; antes disso, o launcher isolado continua sendo a referência.

## dependências externas ao lead

- credenciais OAuth e eventuais limites de conta: usuário;
- escolha de uso/aceitação de risco do OAuth Anthropic: usuário;
- teste visual/operacional no Zed e confirmação de fluxo de sessões: usuário;
- autorização final para substituir instalação global: usuário.
