# sessões independentes e progresso no Zed

status: implementação local e smoke ACP concluídos; validação visual parcial no
Zed confirmou status fora de Thinking e conclusão visível. wake automático e
notificação peer ponta a ponta continuam pendentes. sem alteração global.

## requisitos esclarecidos pelo usuário

- uma sessão deve descobrir outras sessões independentes autorizadas e enviar
  mensagem/prompt como usuário; não se restringe a filhos ou membros da equipe.
- equipes em execução devem mostrar alguma atividade e conclusão no Zed sem
  perguntar ao agente. abrir conversas dos filhos não é requisito mínimo.
- a referência ao Claude Code é expectativa de experiência, não comprovação
  de recurso nativo nem contrato técnico auditado nesta pesquisa.

o antigo escopo que deixava esses itens fora da V2 inicial é histórico; o usuário
agora autorizou investigá-los. isso não aprova instalação ou implementação específica.

## intersessão: base de API existe, função completa não

OpenCode `v1.18.30`:

- `POST /session/:sessionID/message` encaminha `PromptPayload` a
  `SessionPrompt.prompt`; `createUserMessage` persiste mensagem de usuário.
  não há exigência de parentID/equipe nesse handler. sem `noReply:true`, pode
  executar modelo. `/prompt` é identificador de endpoint, não essa rota HTTP.
- `POST /session/:sessionID/prompt_async` inicia a mesma operação em background
  e retorna 204; aceitação não equivale a processamento concluído.
- `GET /session` permanece limitado ao projeto; `scope=project` remove filtro
  de diretório, não reúne todos os projetos. existe `listGlobal` interno, sem
  exposição identificada no grupo SessionApi examinado.
- autenticação de servidor não constitui autorização por sessão/agente.
  faltam descoberta autorizada, ferramenta exposta ao agente e contrato de
  identidade/entrega. não foi encontrada federação entre listeners independentes.
- sessão ocupada: `Runner.ensureRunning` reutiliza o resultado da execução
  existente e ignora novo work. uma mensagem pode ser persistida antes disso;
  não está provado que ganhará um turno posterior separado. não tratar como FIFO,
  rejeição garantida ou entrega confirmada apenas pelo HTTP 204.

fontes fixadas, prefixo:
`https://github.com/anomalyco/opencode/blob/v1.18.30/`

- `packages/opencode/src/server/routes/instance/httpapi/groups/session.ts`
- `packages/opencode/src/server/routes/instance/httpapi/handlers/session.ts`
- `packages/opencode/src/server/routes/instance/httpapi/middleware/authorization.ts`
- `packages/opencode/src/session/prompt.ts`
- `packages/opencode/src/session/session.ts`
- `packages/opencode/src/session/status.ts` e `session/run-state.ts`
- `packages/opencode/src/effect/runner.ts`
- `packages/opencode/test/effect/runner.test.ts`:
  `second ensureRunning ignores new work if already running`.

## progresso: lacuna entre notificações TUI e ACP

Ensemble público no commit `eaf9e84a6e872e6af9ad8bb5a8fd274ce926a878`:
package declara 0.17.0; isso não prova versão instalada no ambiente do usuário.
a inspeção inicial não encontrou instalação Ensemble no projeto V2.

- `team_spawn` cria filho, marca busy/starting, dispara promptAsync e retorna.
- hooks acompanham status de membros; notificações Working/completion são
  `client.tui.showToast`, não atualizações ACP.
- `team_status` é consulta explícita; dashboard localhost é canal separado.
- `team_view` chama `client.tui.selectSession`, não navegação do Zed.

fontes, prefixo:
`https://github.com/hueyexe/opencode-ensemble/blob/eaf9e84a6e872e6af9ad8bb5a8fd274ce926a878/`

- `src/tools/team-spawn.ts`, `src/hooks.ts`, `src/notify.ts`
- `src/tools/team-status.ts`, `src/tools/team-view.ts`, `src/dashboard.ts`

ACP OpenCode 1.18.30 (`packages/opencode/src/acp/` no tag acima):

- `event.ts` encaminha partes/deltas apenas se `ACPSession.tryGet(sessionId)`
  encontra sessão registrada naquela conexão. filho criado internamente não
  entra automaticamente nesse mapa.
- `service.ts` lista raízes (`roots:true`); load/resume registra sessões locais.
- partes de ferramenta do principal conhecido viram `tool_call`/`tool_call_update`;
  isso mostra a chamada spawn, não a vida da equipe em background.
- status idle resolve espera interna; não produz feed genérico de equipe ao ACP.

o protocolo suporta lifecycle de ferramenta, mas não traduz toasts da TUI:
https://agentclientprotocol.com/protocol/v1/tool-calls
https://agentclientprotocol.com/protocol/v1/prompt-turn

docs atuais Zed (não prova da versão instalada):
https://zed.dev/docs/ai/external-agents
https://zed.dev/docs/ai/parallel-agents

conclusão: nos códigos examinados existe lacuna de encaminhamento antes do Zed;
não há evidência para culpar exclusivamente a renderização do cliente. versão
real e comportamento ponta a ponta ainda precisam de confirmação.

## pesquisa anterior · próximo passo histórico

1. identificar versões do ambiente onde o usuário observa team_spawn, sem ler
   credenciais/estado privado; não confundir com V2 ou equipe desta sessão.
2. definir alcance de descoberta entre projetos/processos, autorização e política
   para destinatário ocupado; só então escolher ferramenta/ponte mínima.
3. estudar tradução de estado agregado da equipe para updates ACP da sessão
   principal. não exigir navegação de filhos para cumprir o requisito mínimo.
4. provar com sessões independentes A/B: mensagem aparece como usuário, origem
   identificada, resposta correlacionada; testar B livre e ocupada e alvo não
   autorizado. nenhum sucesso deve ser inferido só de HTTP 204.
5. no Zed: spawn, atividade visível sem pergunta/poll do usuário, conclusão e erro.
   comparar eventos de origem, ACP e tela para localizar perdas.

testes com spawn/prompt executam modelo e exigem autorização própria. essa
restrição foi satisfeita nos smokes autorizados abaixo; o plugin e a ponte locais
agora existem. a implementação não altera o binário oficial nem o Zed.

---

## implementação e smoke local · 2026-09-15

- `v2/plugins/session-bridge.mjs` foi carregado pela configuração V2 e expõe
  `sessions_list`, `sessions_send`, `sessions_receive` e `team_spawn`.
- `opencode-isolated acp` agora passa por `scripts/acp-bridge.py`; o estado fica
  em `.opencode-local/state/session-bridge/` e o PID da ponte identifica a view.
- S-04: smoke A/B real com duas pontes locais confirmou sessão alvo viva,
  `sessions_send`, aviso `session/update` no alvo e `sessions_receive` com o
  marcador. revisão de UX passou a exibir o texto no aviso como `Peer text
  (untrusted)`, sem transformá-lo em mensagem de usuário; origem é atribuída pelo
  contexto e não há HTTP manual no smoke.
- S-05: smoke ACP real confirmou `session/update` durante o turno principal com
  `sessionUpdate=agent_message_chunk`, estados textuais de equipe e `end_turn`.
  o status aparece fora de Thinking; o spinner exato ainda depende do cliente
  Zed.
- testes da implementação: 9 ACP bridge, 10 session bridge/subconfig, além dos
  testes de checker/vault/MarkItDown;
  launcher/config JSON e handshake ACP 1.18.30 OK. não houve build/typecheck.
- limite ainda aberto: reiniciar as duas sessões do Zed e confirmar a renderização
  visual; o smoke ACP não prova o cliente Zed. nenhum commit/push/global.

### snapshot anterior à correção visual · 2026-09-15

- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **37 testes OK**.
- `node --test scripts/test_session_bridge.mjs`: **6 OK**; ponte Python:
  **8 OK**.
- `scripts/s04_smoke.py`: sessão alvo viva registrada, `sessions_send` usado,
  aviso ACP no alvo e `sessions_receive`/marcador confirmados.
- `scripts/s05_smoke.py`: `team_spawn` real via ACP, `session/update` emitido
  durante o turno e `promptStop=end_turn`.
- `scripts/check-v2.py`: **16 agentes, 0 falhas**; `vault-links.py`: **14 notas,
  29 links, 0 duplicatas**; sintaxe shell e JSON OK.
- a validação visual posterior confirmou ferramentas, atividade fora de Thinking
  e mensagem `finished` no Zed após usar o launcher local. isso não prova ainda
  wake automático do pai nem entrega visual de peer em todos os estados.

### ajuste de visibilidade do progresso · 2026-09-15

- após a validação manual, o Zed recolheu `agent_thought_chunk` dentro de
  “Thinking”; `scripts/acp-bridge.py` passou a emitir o status de `team_spawn`
  como `agent_message_chunk`, mantendo o prefixo `[team]` e a sanitização.
- `scripts/s05_smoke.py`: `progressKinds=["agent_message_chunk"]` e
  `promptStop=end_turn`. falta apenas confirmar a nova renderização visual após
  reiniciar o ACP do Zed.

### alinhamento final da rodada · 2026-09-15

- status de equipe foi separado em `queued`, `starting`, `busy`, `idle` e
  `error`, evitando cinco mensagens indistinguíveis para um único filho.
- estados `idle/error` acordam o pai ocioso por prompt interno fixo; durante um
  turno ativo ficam pendentes até a resposta do pai. nenhum payload do filho é
  interpolado nesse prompt.
- peer text continua visível como dado não confiável, mas entra no contexto do
  agente somente por `sessions_receive`, que preserva receipt e validação de
  reply (D-038).
- última regressão: 38 testes Python, 10 testes Node, 9 testes ACP e smoke
  `team_spawn` com `agent_message_chunk`/`end_turn`.
