# limites attach / sessões independentes · V2

data: 2026-09-13. consolidação da pesquisa `SESSIONS-2026-09-11.md`, da spec
ACP e de leitura de código citada nessa pesquisa. Não há arquivo local
`ACP-SESSION-MAP.md`.

## o que funciona (evidência)

| recurso | status | fonte |
|---|---|---|
| `opencode acp` no Zed | mantido pelo escopo informado; teste manual histórico | relato do usuário + `acp --help`; não repetido nesta revisão |
| listar/retomar sessões no Zed | suporte declarado, UI não retestada | ACP spec e leitura de `acp.ts` anunciam `loadSession:true`; não é prova de fluxo no Zed |
| hierarquia de filhos | rota documentada no código, não fluxo de UI provado | leitura de `session.ts` |
| listener HTTP do ACP | comportamento de código documentado | leitura de `acp.ts`; não testado nesta rodada |
| sessionCapabilities anunciadas | comportamento de código documentado | leitura de `acp.ts`: `{close, fork, list, resume}` |

## o que NÃO funciona / não comprovado

| recurso | status | motivo |
|---|---|---|
| mensagens entre sessões independentes | **não comprovado** | `team_message` exige mesma `team_id`; `prompt_async` não entrega fora da equipe |
| descoberta de sessões arbitrárias | **não suportado** | Ensemble só cria filhas com `parentID`; não adota sessões preexistentes |
| UI Zed para subagentes/equipes | **não comprovado** | leitura de código/spec não prova itens navegáveis no Zed; não retestado |
| `attach` a listener HTTP | **hipótese, não testado** | o comportamento sugerido pelo código não foi exercitado com Zed |
| porta fixa `--port` | **risco operacional documentado** | uma mesma porta não pode ser escutada por dois processos; cenário ACP/Zed não retestado |

## arquitetura do listener ACP (hipótese de leitura de código)

```
Zed (ACP client) ──stdio──> opencode-isolated acp --port 4096
                                            │
                                            ▼
                                    HTTP listener (mesmo processo)
                                            │
                                    event bus (sessionUpdate)
                                            │
                                    ┌───────┴───────┐
                                    ▼               ▼
                              sessão A         sessão B (filha)
```

Hipótese a validar: ambas as sessões teriam de ser criadas/carregadas naquele
listener (`load`/`new`/`resume`/`fork` naquele processo), e eventos
`sessionUpdate` seriam encaminhados à conexão Zed correspondente. O diagrama
não documenta uma execução ponta a ponta.

## escopo informado para a V2 inicial

Este escopo vem do resumo fornecido pelo usuário e do estado registrado no
backlog; não registra uma nova decisão nem prova os fluxos de UI.

| item | estado informado | justificativa |
|---|---|---|
| `acp` no Zed | **manter** | estado informado pelo usuário; há evidência manual histórica, sem reteste nesta revisão |
| `attach` / segunda janela TUI | **fora da V2 inicial** | hipótese não testada; porta fixa colide; não resolve mensageria inter-sessão |
| mensageria entre sessões independentes | **fora da V2 inicial** | exige gateway/coordination layer não existente; ACP nativo não entrega |
| visibilidade filhos/equipes no Zed | **fora da V2 inicial** | UI correspondente não foi validada; não prometer visibilidade de filhos/equipes |
| Ensemble | **fora da V2 inicial** | pesquisa documental não encontrou adoção de sessões preexistentes; não houve validação local ou de UI |

## próxima etapa se o usuário quiser avançar

1. testar `attach` real com Zed aberto (precisa autorização, custo de modelo).
2. se quiser mensageria real: avaliar gateway ACP dedicado ou contribuição upstream.
3. por enquanto, documentar limitação e não prometer.

## arquivos relacionados

- `docs/additive/SESSIONS-2026-09-11.md` — pesquisa Ensemble + correção hipótese
- `docs/core/BACKLOG.md` — E6 aberto, D-021 não implementada

## estado atual do bridge local · 2026-09-15

O texto acima preserva a fotografia histórica da pesquisa de 2026-09-13. Desde
então, o launcher V2 possui um bridge local que comprova, no mesmo projeto,
`sessions_list`, `sessions_send`, `sessions_receive` e `team_spawn` entre
processos ACP. Isso não transforma a API nativa em federação global: cross-
project, FIFO, entrega garantida e navegação completa de filhos continuam fora
da prova. Consulte `docs/core/LOGIC.md` e o registro S-04/S-05 no backlog para o
estado executável atual.
