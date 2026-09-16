# capacidades transversais · avaliação documental

## alcance e evidência

pedido: atender desenvolvimento, suporte/automação, pesquisa/planejamento e
design/UI, incluindo MCPs como capacidades; avaliar Exa Search, RTK,
MarkItDown e Sequential Thinking para todos os arquétipos.

pesquisa somente leitura, delegada a dois agentes, com Context7 seguido de
fontes oficiais. nenhum pacote instalado, MCP iniciado ou comando abaixo
testado localmente. documentação atual não comprova a versão do legado.
busca nos markdowns permitidos não encontrou uso de RTK/Sequential Thinking;
isso não prova ausência no runtime. inventário efetivo dos quatro segue aberto.

## extração útil das interfaces documentadas

| capacidade | interface útil | finalidade e limite |
| --- | --- | --- |
| Exa | `web_search_exa`, `web_fetch_exa` | busca e recuperação web; HTTPS remoto, consultas saem da máquina |
| Exa opcional | `web_search_advanced_exa`, `agent_run` | busca avançada e execução multi-etapas; não incluir por padrão sem prova de necessidade/custo |
| RTK, CLI Rust | `rtk git status`, `rtk git diff`, `rtk git log` | resumir inspeção git |
| RTK | `rtk test <cmd>`, `rtk pytest`, `rtk cargo test`, `rtk tsc` | reduzir saída de testes/typecheck; não remove limites de recursos da máquina |
| RTK | `rtk docker ps`, `rtk gh pr list` | resumir inventários; rede/permissões dependem do comando encapsulado |
| RTK | `rtk gain`, `rtk recall <hash>`, `rtk proxy <cmd>` | métricas estimadas, recuperação de saída armazenada e execução sem filtragem; validar na versão escolhida |
| MarkItDown CLI | `markitdown input.pdf -o output.md` | converter documento local; preferir extras mínimos para formatos necessários |
| MarkItDown | `markitdown --list-plugins` | listar plugins; não habilitar terceiros automaticamente |
| MarkItDown MCP | `convert_to_markdown(uri)` | aceita `file:`, `http:`, `https:`, `data:`; amplia acesso a arquivos e rede |
| Sequential Thinking MCP | `sequential_thinking` | organizar etapas/revisões/ramificações; não verifica fatos nem garante raciocínio melhor |

Sequential Thinking: campos obrigatórios `thought`, `nextThoughtNeeded`,
`thoughtNumber`, `totalThoughts`; opcionais `isRevision`, `revisesThought`,
`branchFromThought`, `branchId`, `needsMoreThoughts`. conteúdo estruturado
deve ser plano/hipóteses/resumos úteis, não requisito de expor raciocínio interno.
`DISABLE_THOUGHT_LOGGING=true` é documentado; validar efeito antes de uso.

## matriz proposta, não aprovada

alto/médio/baixo indica utilidade esperada, não frequência obrigatória.

| arquétipo/papel | Exa | RTK | MarkItDown | Sequential Thinking |
| --- | --- | --- | --- | --- |
| lovelace · desenvolvimento | alto: pesquisa técnica | alto: git/testes | médio: specs | médio: debug/arquitetura |
| aurel · suporte/automação | alto: erros/advisories | alto: saídas repetitivas | médio: documentos | médio: hipóteses diagnósticas |
| creator-ux · design/UI | alto: referências | baixo/médio: testes | alto: briefs | médio: fluxos/estados |
| pesquisa/planejamento · papel | alto: fontes | baixo | alto: normalização | médio/alto: decomposição |
| QA/revisão · papel | médio: fontes atuais | alto, com evidência integral | médio: relatórios | médio: cobertura/alternativas |

os três nomes vêm dos docs locais consultados; os dois últimos são papéis
analíticos, não novos agentes aprovados.

## simplificações propostas

checkpoint: usuário autorizou registrar a avaliação e compactar o contexto.
não escolheu ainda entre: (1) Exa/Sequential Thinking MCP + RTK/MarkItDown CLI;
(2) incluir também MarkItDown MCP; (3) comparar antes de escolher.
recomendação do assistente: opção 1. retomar por essa decisão, sem ativação
implícita e preservando os gates do backlog.

- disponibilidade transversal não obriga chamada em toda tarefa.
- Exa: começar com busca/fetch; não adicionar `agent_run` e mais uma camada de
  delegação sem benefício medido. Context7, se aprovado separadamente, serviria
  docs específicas; Exa cobriria descoberta e lacunas. não consultar ambos
  mecanicamente.
- RTK: utilitário local, não MCP. validar manualmente antes de hook automático;
  hook Bash não comprime ferramentas nativas Read/Grep/Glob nem system prompt.
- MarkItDown: preferir CLI local para documentos, não servidor HTTP permanente.
  MCP STDIO é alternativa se trouxer ergonomia comprovada. não duplicar fetch
  de HTML comum quando Exa/ferramenta existente já entrega texto adequado.
- Sequential Thinking: comparar com plano curto/todowrite nativo. manter como
  opção complexa somente se melhorar resultado, não por quantidade de etapas.
- não prometer descoberta/carregamento dinâmico: depende de teste do runtime.

## riscos e gates antes de ativar

- Exa: conteúdo web é não confiável; não enviar documentos privados/segredos.
  autenticação, orçamento, quota anônima e limites efetivos MCP estão pendentes;
  limites da API REST não devem ser tratados como quota do MCP.
- RTK: compressão pode ocultar evidência. diagnóstico/QA precisam acesso à saída
  integral quando necessário. recall persiste stdout e pode guardar conteúdo
  sensível. há divergência documental sobre telemetria; fixar versão e verificar
  comportamento/configuração, sem presumir padrão seguro. economia anunciada
  de até 90% refere-se a saída Bash, não à conta/contexto total; tokens são
  estimados, não medição de faturamento.
- MarkItDown: execução local não é sandbox nem garantia de ausência de rede.
  URIs, plugins e integrações externas podem introduzir egress/custo; servidor
  HTTP sem autenticação expõe acesso com permissões do processo. preferir CLI
  ou STDIO, sem bind externo. limitar formatos/tamanho e testar extração;
  Markdown não substitui inspeção visual de layout/gráficos.
- Sequential Thinking: chamadas acrescentam texto/latência; logs podem persistir
  dados. não usar como fonte de verdade nem substituir testes.

## aceitação proposta

1. confirmar versão/interface de cada componente, origem e permissões mínimas.
2. Exa: pesquisa pública com fontes rastreáveis; observar erros/quota sem envio
   privado e limitar tamanho das respostas.
3. RTK: comparar comando bruto e filtrado em sucesso/falha; verificar status de
   saída, evidência preservada, persistência e telemetria.
4. MarkItDown: converter fixtures públicas PDF/DOCX/XLSX, conferir conteúdo,
   tabelas/perdas e consumo de recursos; não presumir fidelidade visual.
5. Sequential Thinking: comparar tarefa complexa com/sem MCP por correção,
   latência e contexto; verificar política de logs, sem exigir chain-of-thought.
6. migrar isoladamente só após gates do backlog; nenhuma mudança global.

## fontes

- https://docs.exa.ai/reference/exa-mcp
- https://github.com/exa-labs/exa-mcp-server
- https://docs.exa.ai/reference/search
- https://github.com/microsoft/markitdown
- https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp
- https://github.com/rtk-ai/rtk
- https://github.com/rtk-ai/rtk/blob/develop/docs/guide/resources/savings-explained.md
- https://github.com/rtk-ai/rtk/blob/develop/docs/guide/getting-started/configuration.md
- https://github.com/rtk-ai/rtk/blob/develop/docs/usage/AUDIT_GUIDE.md
- https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking
