# PROCESSO DE INÍCIO DE PROJETO

**Versão:** 1.1 · **Data:** 07/09/2026 · **Substitui:** `docs/pdf/PROJETO_NOVO.pdf`
**Escopo:** qualquer projeto de software da casa, em qualquer stack, desenvolvido com Claude Code + Agent Teams.

Este documento é o método. Ele não diz *o que* um sistema faz (isso é o spec de cada projeto) nem *como* os agentes se organizam por padrão (isso é o `~/.claude/CLAUDE.md` global). Ele diz **em que ordem as coisas acontecem, quem decide cada uma, e quais regras de engenharia valem em todas elas**.

---

## 0. As três camadas e o princípio único

```
GLOBAL      ~/.claude/CLAUDE.md      COMO trabalhamos (equipe, QA, security, review, tetos de máquina)
PROJETO     /projeto/CLAUDE.md       O QUE este sistema é (stack, comandos, regras críticas, proibições)
            /projeto/docs/*.md       Fonte da verdade detalhada
TAREFA      sua mensagem             O QUE fazer agora
```

O princípio que sustenta tudo:

> **Nunca acelere pulando entendimento. Acelere paralelizando execução.**

Cinco agentes escrevendo código sobre uma arquitetura não aprovada produzem cinco vezes mais retrabalho. O ganho vem de: **arquitetura aprovada + backlog com dependências explícitas + ownership de arquivos + verificação independente**.

### Divisão de responsabilidades

| Você (humano) | Claude (Lead) + agentes |
|---|---|
| Fornece fontes | Analisa, documenta, propõe |
| Decide produto e negócio | Decide técnica rotineira |
| Aprova arquitetura (gate) | Cria backlog, implementa, testa |
| Aprova deploy em produção (gate) | Audita, corrige, retesta, documenta |
| Muda prioridades | Mantém docs sincronizadas com o código |

Existem **apenas três gates humanos obrigatórios**: pendências de negócio (04), arquitetura (05) e deploy (14). Todo o resto flui sem você.

---

## 1. O que muda em relação ao PDF anterior

O fluxo de 16 etapas está preservado. O que este documento acrescenta:

1. **Fase 00 (Bootstrap)**: como nasce o repositório antes de qualquer fonte ser lida. O PDF começava com o repo já existindo.
2. **Normas de engenharia transversais** (seção 3): KISS, YAGNI, comentários, revisão, otimização. Valem em toda etapa, e os prompts as referenciam.
3. **Catálogo de falhas típicas de IA em código** (seção 4): a lista do que revisores devem procurar ativamente, não por acaso.
4. **Definition of Ready / Definition of Done** por etapa: critérios objetivos para saber que uma fase terminou.
5. **Prompts limpos**: o prompt de implementação do PDF continha um texto colado de outro projeto (alterações no módulo de turismo). Foi removido.
6. **Ownership explícito** como pré-requisito de paralelismo, não como recomendação.
7. **Perfis de projeto** (seção 6): qual subconjunto do fluxo usar para projeto novo, epic nova, bug e ajuste visual.

---

## 2. O fluxo completo

```
00 BOOTSTRAP            VOCÊ + CLAUDE   repositório, docs/fontes, .gitignore, primeiro commit
01 INPUT                VOCÊ            coloca as fontes em docs/fontes/
02 DISCOVERY            CLAUDE          entende sem programar
03 DOCUMENTAÇÃO INICIAL CLAUDE          PRODUCT, REQUIREMENTS, FLOWS, DATA-MODEL, ARCHITECTURE (proposta), ACCEPTANCE, DECISIONS
04 PENDÊNCIAS           CLAUDE pergunta / VOCÊ decide          ← GATE
05 ARQUITETURA          CLAUDE propõe / VOCÊ aprova            ← GATE
06 CONSOLIDAÇÃO         CLAUDE          docs coerentes com decisões e arquitetura
07 CLAUDE.md DO PROJETO CLAUDE          conciso, operacional, referencia docs/
08 BACKLOG              CLAUDE          epics, tasks, dependências, ownership, paralelismo
09 IMPLEMENTAÇÃO        LEAD + AGENT TEAM
10 VERIFICAÇÃO          QA + SECURITY + FINAL REVIEW (paralelo, só reportam)
11 CORREÇÕES            LEAD roteia para o dono do módulo
12 REGRESSÃO            QA + SECURITY repetem o que falhou      ↻ volta a 11 se necessário
13 RELEASE CANDIDATE    CLAUDE          testes, lint, typecheck, build, migrations, config
14 APROVAÇÃO DE DEPLOY  VOCÊ                                    ← GATE
15 DEPLOY + SMOKE       CLAUDE
16 DOCUMENTAÇÃO FINAL   CLAUDE          RUNBOOK, CHANGELOG, backlog marcado, docs atualizadas
17 TRANSIÇÃO            CLAUDE          limpeza, memória, ondas da próxima etapa, Trello   ↻ volta a 09
```

A partir da segunda etapa o ciclo é 17 → 09 → … → 16 → 17, para sempre. Seção 9 detalha.

---

## 3. Normas de engenharia (valem em todas as etapas)

Estas regras são citadas nos prompts como "as normas de engenharia do processo". Não repita o conteúdo nos prompts; referencie esta seção.

### 3.1 Simplicidade

- **KISS.** A solução mais simples que satisfaz o requisito é a correta. Complexidade precisa de justificativa escrita em DECISIONS.md.
- **YAGNI.** Não implemente o que não está no backlog. Não crie abstração para "o futuro". Não adicione parâmetro, flag, config ou camada que nenhum caso de uso atual exige.
- **Não introduza dependência para resolver o que 20 linhas resolvem.** Toda dependência nova entra em DECISIONS.md com motivo e alternativa considerada.
- **Um conceito, um nome, um lugar.** Se o domínio já tem "Licença", não crie "Assinatura" para a mesma coisa. Regras de negócio ficam centralizadas e testáveis, nunca espalhadas em handlers e componentes.

### 3.2 Código

- **Sem comentários explicando o que o código faz.** Nome bom substitui comentário. Comentário só para *por que* algo não-óbvio existe (workaround de bug de terceiro, invariante de negócio sutil, referência a decisão). Comentários do tipo "// incrementa contador", "// TODO depois", "// função auxiliar" são proibidos.
- **Sem código morto.** Nada de função não chamada, import não usado, bloco comentado "para referência", feature flag que nunca é ligada.
- **Sem defensividade cega.** Não envolva tudo em try/catch que engole erro. Não valide o que o tipo já garante. Não cheque `null` em campo que o schema declara obrigatório. Erros devem falhar alto, cedo, com mensagem útil.
- **Funções pequenas, com um propósito.** Se precisa de "e" para descrever, são duas funções.
- **Siga a convenção do repositório, não a sua preferência.** Nomenclatura, estrutura de pastas, estilo de import, forma de tratar erro: olhe três arquivos existentes antes de criar o quarto.
- **Tipos fortes nas fronteiras.** Entrada de API, payload de webhook, variável de ambiente, retorno de banco: tudo validado em runtime na borda e tipado dentro. Nada de `any`, `dict` solto ou `interface{}` atravessando o sistema.
- **Idempotência em tudo que pode ser reexecutado:** webhooks, jobs, migrations, scripts de seed, retries.

### 3.3 Dados e estado

- **Migrations são imutáveis depois de aplicadas.** Nova mudança, nova migration. Nunca edite uma migration que já rodou em qualquer ambiente.
- **Soft delete quando existe histórico relacionado.** Exclusão física só quando o spec pede explicitamente.
- **Invariantes de negócio no banco quando possível** (unique, check, FK), na aplicação sempre, nos testes obrigatoriamente.
- **Sem lógica de negócio em componente de UI, controller ou handler de rota.** Essas camadas orquestram; a regra mora em serviço de domínio.

### 3.4 Segurança por padrão

- Toda rota nasce **autenticada e autorizada**. Rota pública é exceção declarada.
- Autorização checa **posse do recurso**, não só o papel. "É admin" não basta; "esse cliente é dono dessa licença" é a pergunta.
- **Segredos nunca no código nem no git.** Nunca em log. Nunca em mensagem de erro para o usuário.
- Entrada do usuário é hostil até prova em contrário. Query parametrizada sempre. Escape na saída sempre. Upload com validação de tipo, tamanho e nome.
- Mensagem de erro para o usuário é genérica; detalhe vai para o log.

### 3.5 Testes

- Testa-se **comportamento**, não implementação. Teste que quebra ao renomear uma função privada é teste ruim.
- Prioridade: **invariantes de negócio e dinheiro** primeiro, fluxos críticos depois, o resto por último.
- Toda correção de bug entra com **um teste que falhava antes e passa depois**. Sem exceção.
- Teste que passa mas não testa nada (sem assert, assert trivial, mock do que está sendo testado) é pior que ausência de teste, porque dá falsa segurança.
- **Nunca ajuste o teste para passar.** Se o teste está errado, corrija o teste e explique em uma linha no commit. Se o código está errado, corrija o código.

### 3.6 Otimização

- **Meça antes.** Otimização sem número é chute. Otimização prematura é dívida.
- As únicas otimizações permitidas sem medição são as estruturais óbvias: índice em coluna filtrada, evitar N+1, paginar listas, não carregar o que não vai usar, não fazer no loop o que pode ser feito uma vez fora dele.
- Cache é a última ferramenta, não a primeira. Cache introduz invalidação, e invalidação introduz bugs invisíveis.

### 3.7 Revisão de código

Toda mudança substancial passa por revisor **independente do autor** (agente diferente ou sessão diferente). O revisor:

1. Lê o requisito antes de ler o diff.
2. Verifica que o diff faz **exatamente** o requisito: nem menos (incompleto), nem mais (scope creep).
3. Roda o código, não só lê. Para web, abre no navegador.
4. Procura ativamente o catálogo da seção 4.
5. Reporta findings ao Lead com severidade, arquivo, linha e cenário de falha. **Não corrige código de outro dono.**
6. Não aprova por cansaço. "Parece ok" não é aprovação.

### 3.8 Git

- Branch por epic ou por task, nunca commit direto em `main` durante desenvolvimento.
- Commit pequeno, mensagem no imperativo, primeira linha até 72 caracteres, corpo explicando *por que* quando não for óbvio.
- Nunca `--force` em branch compartilhada. Nunca `git add .` sem olhar `git status` antes.
- `.gitignore` antes do primeiro commit. Se um segredo entrou no histórico, o segredo está comprometido: rotacione, não só remova.

---

## 4. Onde IAs falham ao escrever código (checklist de revisão)

Esta lista existe porque os erros são **sistemáticos**, não aleatórios. Revisores devem procurar cada item. Implementadores devem se autoverificar contra ela antes de reportar conclusão.

### 4.1 Invenção

- Inventa requisito que não está no spec ("achei que faria sentido ter…").
- Inventa campo no modelo de dados sem caso de uso.
- Inventa endpoint, permissão ou estado que ninguém pediu.
- Inventa API de biblioteca: chama método que não existe naquela versão, ou usa assinatura de outra versão.
- Inventa que testou: relata "testes passando" sem ter executado, ou executou um subconjunto e generalizou.

**Contramedida:** todo requisito implementado aponta para um ID em REQUIREMENTS.md. Toda afirmação de teste vem com o comando executado e a saída.

### 4.2 Simplificação silenciosa

- Remove uma regra de negócio porque "complicava o código".
- Troca "uma cobrança por licença" por "uma cobrança por cliente" porque era mais fácil de modelar.
- Ignora um caso de borda do spec (cliente com duas licenças do mesmo produto, território liberado e reocupado) e implementa só o caminho feliz.
- Resolve ambiguidade escolhendo o comportamento mais conveniente, sem registrar.

**Contramedida:** ambiguidade vira PENDENTE DE DECISÃO em DECISIONS.md, nunca escolha silenciosa. Revisor compara ACCEPTANCE.md contra o comportamento real.

### 4.3 Excesso

- Cria abstração genérica para um caso de uso (`BaseRepository<T>`, `AbstractHandlerFactory`).
- Adiciona camada de indireção "para facilitar testes" que ninguém testa.
- Escreve helper de 40 linhas para o que a stdlib faz em 1.
- Adiciona dependência nova para funcionalidade trivial.
- Comenta cada linha, escreve docstring em getter, adiciona cabeçalho de arquivo.
- Cria README, CONTRIBUTING, exemplo, script de conveniência que ninguém pediu.

**Contramedida:** YAGNI é norma, não sugestão. Revisor pergunta de cada arquivo novo: "qual task do backlog pediu isso?"

### 4.4 Inconsistência

- Usa três estilos de tratamento de erro no mesmo módulo.
- Nomeia a mesma coisa de dois jeitos em arquivos diferentes.
- Cria um segundo utilitário que já existia no repo com outro nome.
- Muda a convenção do repositório sem perceber (camelCase num projeto snake_case, default export num projeto de named exports).
- Deixa o modelo de dados divergente entre migration, ORM, tipo do frontend e docs.

**Contramedida:** ler três arquivos vizinhos antes de criar um. Buscar por nome antes de criar utilitário. Uma fonte de verdade para o modelo de dados, geração de tipos quando a stack permite.

### 4.5 Segurança

- Rota nova sem autenticação porque "copiei de outra que era pública".
- Autorização checa papel mas não posse (qualquer cliente logado acessa qualquer licença por ID).
- Concatena string em query "só nesse caso".
- Loga payload inteiro incluindo token, senha ou CPF.
- Aceita webhook sem validar assinatura/token de origem.
- Retorna stack trace ou mensagem interna para o cliente.
- Gera token, ID ou senha com fonte não criptográfica.

**Contramedida:** seção 3.4 é checklist obrigatória do security-reviewer para cada rota, webhook e job novos.

### 4.6 Concorrência e estado

- Ignora condição de corrida em operação que precisa ser exclusiva (dois checkouts do mesmo território ao mesmo tempo).
- Webhook processado duas vezes gera efeito duplo.
- Job que falha no meio deixa estado parcial sem rollback ou sem marcação.
- Usa estado global mutável ou singleton com estado em ambiente com concorrência.

**Contramedida:** todo processo financeiro e todo webhook tem teste de idempotência. Operações exclusivas usam lock ou constraint de banco, não checagem-depois-escrita.

### 4.7 Ambiente e infraestrutura

- Hardcoda URL, porta, caminho, credencial de desenvolvimento.
- Assume que o ambiente de execução é igual ao de desenvolvimento.
- Não documenta variável de ambiente nova, e o deploy quebra.
- Roda comando pesado (build, typecheck, suíte inteira) sem verificar carga da máquina, em paralelo com outros agentes. **Ver teto no CLAUDE.md global: máximo 3 typechecks e 3 builds simultâneos na máquina inteira.**
- Executa migration ou comando destrutivo em banco sem confirmar qual banco é.

**Contramedida:** toda variável nova entra no RUNBOOK e no `.env.example` no mesmo commit. Comando pesado só depois de contar processos e olhar `free -h`.

### 4.8 Relato

- Declara "concluído" quando só o código foi escrito.
- Declara "corrigido" quando só alterou o código, sem retestar o cenário que falhou.
- Resume tool output de forma otimista, omitindo warnings, testes pulados ou erros "não relacionados".
- Diz "não há regressões" sem ter rodado a suíte.

**Contramedida:** Definition of Done da seção 5. Relato final sempre inclui comandos executados e saída resumida, pendências e riscos, não só sucessos.

---

## 5. As etapas em detalhe

Cada etapa de procedimento tem uma skill global que carrega o prompt e o DoD automaticamente. Prefira a skill a colar o prompt:

| Etapa | Skill | Etapa | Skill |
|---|---|---|---|
| 00 | `/projeto-bootstrap` | 07 | `/project-claude-md` |
| 02–03 | `/discovery` | 08 | `/backlog` |
| 04 | `/pendencias` | 09–12 | `/epic <id>` |
| 05–06 | `/arquitetura` | 13 | `/release-candidate` |
| | | 16 | `/docs-finais` |
| | | 17 | `/proxima-etapa <E-X>` |

Os prompts abaixo permanecem como referência e para uso fora do Claude Code.

Cada etapa traz: responsável, objetivo, prompt padrão, Definition of Done (DoD). Os prompts são para copiar. Onde diz "normas de engenharia do processo", o Lead lê a seção 3 deste documento.

---

### 00. BOOTSTRAP

**Responsável:** você cria a pasta e o remoto; Claude faz o resto.

**Objetivo:** ter um repositório limpo, com estrutura de docs, gitignore e primeiro commit, antes de qualquer fonte ser lida.

**Prompt padrão:**

```text
Inicialize este repositório para um projeto novo seguindo docs/PROCESSO_INICIO_PROJETO.md (ou o processo global de início de projeto).

Ainda não conhecemos a stack. Não crie código de aplicação.

Crie:
- .gitignore genérico (SO, editores, .env, node_modules, __pycache__, dist, build, coverage, logs)
- .env.example vazio com comentário de cabeçalho
- docs/fontes/ (vazia, com .gitkeep)
- docs/referencias/ (vazia, com .gitkeep)
- README.md mínimo: nome do projeto, uma linha de propósito, ponteiro para docs/
- CLAUDE.md provisório contendo apenas: "Projeto em fase de discovery. Fonte da verdade: docs/. Não implementar código até ARCHITECTURE.md ser aprovada."

Faça o primeiro commit: "chore: inicializa repositório <nome> com estrutura de documentação".
```

**DoD:**
- `git log` mostra um commit.
- `.gitignore` cobre `.env`.
- Nenhum arquivo de código de aplicação existe.

---

### 01. INPUT

**Responsável:** você.

**Objetivo:** dar a Claude tudo que representa a realidade do projeto.

Coloque em `docs/fontes/`: PDF, MD, DOC, prints, wireframes, briefing, documentos do cliente, regras de negócio, exemplos, dump de sistema antigo, planilhas, código existente, referências visuais.

**Regras:**
- Esses arquivos são **fontes**. Claude nunca os modifica.
- Prefira `.md` a PDF quando existir. PDF é para leitura humana; `.md` é para o agente. Em divergência, o `.md` prevalece (registre isso no próprio doc).
- Se há um spec principal, nomeie-o de forma inequívoca e declare-o como fonte da verdade no cabeçalho.
- Ainda **não peça para programar**.

**DoD:** você consegue listar em uma frase o que cada arquivo em `docs/fontes/` é.

---

### 02. DISCOVERY

**Responsável:** Claude.

**Objetivo:** entender profundamente antes de escrever qualquer código.

**Prompt padrão:**

```text
Quero iniciar este projeto seguindo nosso workflow global de desenvolvimento e o processo de início de projeto.

FASE ATUAL: DISCOVERY.

Leia integralmente todos os materiais em docs/fontes/ e docs/referencias/, o CLAUDE.md, e analise qualquer código existente neste repositório.

Não implemente nem altere código nesta etapa. Não modifique docs/fontes/.

Identifique:
- objetivo do produto
- usuários e perfis
- módulos
- funcionalidades
- regras de negócio (com atenção especial a dinheiro, permissões, estados e exclusividade)
- fluxos
- entidades e dados
- permissões
- integrações externas
- requisitos funcionais e não funcionais
- dependências externas
- pontos contraditórios entre fontes
- informações ausentes
- decisões que ainda precisam ser tomadas

Regras:
- Não invente informações ausentes. O que não está nas fontes é PENDENTE DE DECISÃO.
- Quando duas fontes divergem, cite ambas e marque como CONTRADIÇÃO.
- Distinga fato confirmado nas fontes de inferência sua.

Ao terminar, avance automaticamente para a geração da documentação inicial.
```

**DoD:** a lista de pendências e contradições existe e está separada dos fatos. Nenhum arquivo de código foi tocado.

---

### 03. DOCUMENTAÇÃO INICIAL

**Responsável:** Claude.

**Objetivo:** transformar fontes heterogêneas em documentação operacional e rastreável.

**Prompt padrão** (geralmente continuação automática de 02):

```text
Com base exclusivamente nas fontes analisadas e no que foi possível confirmar, gere a documentação inicial do projeto.

Crie:
docs/PRODUCT.md        visão, público, proposta de valor, o que NÃO é
docs/REQUIREMENTS.md   requisitos com ID (RF-xxx funcional, RNF-xxx não funcional), fonte de cada um
docs/FLOWS.md          fluxos principais e de erro, passo a passo
docs/DATA-MODEL.md     entidades, campos, relações, invariantes, estados e transições
docs/ARCHITECTURE.md   PROPOSTA (marcada como não aprovada no cabeçalho)
docs/ACCEPTANCE.md     critérios de aceite com ID (AC-xxx), objetivos e testáveis, ligados a RF
docs/DECISIONS.md      decisões tomadas (com data e quem decidiu) e PENDENTES DE DECISÃO

Regras:
1. Não invente requisitos.
2. Separe claramente: fato confirmado / proposta técnica / pendência.
3. ARCHITECTURE.md nesta etapa é PROPOSTA, não arquitetura aprovada.
4. Cada requisito em REQUIREMENTS.md cita a fonte (arquivo e seção).
5. Cada critério em ACCEPTANCE.md é verificável por alguém sem contexto: dado X, quando Y, então Z.
6. Em DATA-MODEL.md, nenhum campo sem um requisito que o exija.
7. Todas as questões abertas vão para DECISIONS.md com contexto.
8. Preserve docs/fontes/ intacta.
9. Siga as normas de engenharia do processo: sem excesso, sem abstração especulativa na proposta de arquitetura.
```

**DoD:** os sete arquivos existem. Todo RF tem fonte. Todo AC aponta para um RF. Toda pendência está em DECISIONS.md e não espalhada nos outros docs.

---

### 04. PENDÊNCIAS E DECISÕES · GATE HUMANO

**Responsável:** Claude pergunta, você decide.

**Objetivo:** resolver o que só o dono do produto pode resolver, e nada além disso.

**Prompt padrão:**

```text
Agora faça a etapa de resolução de pendências.

Revise toda a documentação inicial e apresente SOMENTE decisões que realmente precisem da minha intervenção: negócio, produto, prioridade, dinheiro, dados sensíveis, integrações com custo.

Não me pergunte decisões técnicas rotineiras que você consiga determinar com segurança pela arquitetura, boas práticas ou pelo próprio projeto. Decida essas sozinho e registre em DECISIONS.md como "decisão técnica do Lead".

Para cada decisão necessária, apresente:
1. contexto
2. o que não está definido
3. opções possíveis
4. impactos de cada opção
5. sua recomendação (uma só)
6. a pergunta objetiva que eu preciso responder

Agrupe em blocos por tema. Numere. Mantenha cada bloco curto.

Depois das minhas respostas, registre cada decisão em docs/DECISIONS.md com data e atualize os demais documentos afetados.
```

**Formato esperado de cada pergunta:**

```text
DECISÃO 03 · Exclusão de clientes

A) exclusão definitiva
B) desativação (soft delete)
C) arquivamento

Recomendação: B. Existem propostas e faturas relacionadas ao cliente.

Qual comportamento deseja?
```

Você responde `B`. Claude registra e propaga.

**DoD:** DECISIONS.md não tem mais item PENDENTE que bloqueie arquitetura. Pendências não bloqueantes podem ficar, marcadas como tal.

---

### 05. ARQUITETURA · GATE HUMANO

**Responsável:** Claude propõe, você aprova.

**Objetivo:** fixar a arquitetura antes que qualquer agente paralelo a solidifique.

> Agentes paralelos aceleram uma arquitetura boa. Também aceleram uma arquitetura ruim.

**Prompt padrão:**

```text
Com requisitos e decisões consolidados, proponha a arquitetura definitiva do sistema.

Ainda não implemente.

Defina conforme necessário:
- stack (linguagem, framework, ORM, banco, runtime) com justificativa de uma linha cada
- organização de frontend e de backend
- modelo de dados (refinando DATA-MODEL.md)
- autenticação, autorização, RBAC
- APIs e contratos entre frontend e backend
- integrações externas e como serão isoladas
- armazenamento de arquivos
- filas, jobs, agendamentos
- cache (só se houver requisito que o exija)
- segurança
- observabilidade e logs
- estratégia de testes (o que é unitário, integração, E2E)
- infraestrutura e deploy
- estrutura de diretórios
- fronteiras entre módulos e quem pode importar quem

Regras:
- Não introduza tecnologia sem requisito que a justifique.
- Priorize simplicidade, segurança, manutenção e velocidade de desenvolvimento, nesta ordem.
- Se o repositório já tem stack, preserve-a salvo incompatibilidade real com os requisitos.
- Cada decisão arquitetural relevante tem motivo em uma ou duas frases e alternativa descartada.
- Siga as normas de engenharia do processo.

Ao final, apresente separadamente:
ARQUITETURA RECOMENDADA
RISCOS
TRADE-OFFS
DECISÕES QUE AINDA PRECISAM DE MIM

Não implemente até eu aprovar.
```

**Sua resposta:** `Arquitetura aprovada.` ou `Aprovada, mas quero PostgreSQL em vez de MySQL.`

**DoD:** ARCHITECTURE.md tem cabeçalho "APROVADA em <data> por <nome>". Stack está fixada. Fronteiras de módulo estão nomeadas.

---

### 06. DOCUMENTAÇÃO CONSOLIDADA

**Responsável:** Claude.

**Prompt padrão:**

```text
Arquitetura aprovada.

Consolide toda a documentação do projeto conforme a arquitetura aprovada e as decisões tomadas.

Atualize onde necessário: PRODUCT, REQUIREMENTS, FLOWS, DATA-MODEL, ARCHITECTURE, ACCEPTANCE, DECISIONS.

Remova das seções de pendência o que já foi decidido. Garanta consistência entre documentos: mesmo nome para a mesma entidade, mesmo estado com o mesmo significado, nenhum requisito órfão.

Ainda não comece a implementação.
```

**DoD:** grep por "PENDENTE" nos docs retorna apenas pendências reais e não bloqueantes. Um leitor novo entende o sistema só pelos docs.

---

### 07. CLAUDE.md DO PROJETO

**Responsável:** Claude.

**Objetivo:** o arquivo que todo agente lê em toda sessão. Curto, operacional, sem duplicar docs/.

**Prompt padrão:**

```text
Agora crie ou atualize o CLAUDE.md específico deste projeto, substituindo o provisório.

Deve ser conciso e operacional. Não copie a documentação para dentro dele; referencie docs/ como fonte detalhada.

Inclua somente o que um agente precisa saber SEMPRE que trabalhar aqui:
- descrição do projeto em duas linhas
- onde está a documentação oficial e qual arquivo é fonte da verdade
- stack e versões
- estrutura principal de diretórios e fronteiras de módulo
- regras de negócio críticas (as que, se violadas, causam prejuízo ou dado inconsistente)
- regras de segurança e RBAC em forma de checklist
- convenções (nomenclatura, tratamento de erro, onde mora regra de negócio)
- comandos: dev, teste, lint, typecheck, build, migrations, seed, deploy
- variáveis de ambiente obrigatórias (nomes, nunca valores)
- o que NUNCA fazer neste projeto (lista explícita)
- ponteiro para as normas de engenharia do processo de início de projeto

Este CLAUDE.md complementa, e não substitui, as instruções globais em ~/.claude/CLAUDE.md.
```

**DoD:** CLAUDE.md cabe em uma tela e meia. Todo comando listado foi executado com sucesso ao menos uma vez.

---

### 08. BACKLOG

**Responsável:** Claude.

**Objetivo:** transformar o projeto em trabalho executável e paralelizável **sem conflito de arquivo**.

**Prompt padrão:**

```text
Com documentação e arquitetura aprovadas, transforme o projeto em um backlog implementável.

Ainda não implemente.

Organize em EPICS > TASKS > SUBTASKS (quando necessário).

Para cada task defina:
- ID (E-1-T003)
- objetivo em uma frase
- requisitos atendidos (RF-xxx) e critérios de aceite cobertos (AC-xxx)
- responsável lógico (backend-engineer, frontend-engineer, senior-engineer)
- complexidade: normal | alta (alta = dinheiro, concorrência, integração externa, webhook, migração de dados, refactor estrutural; vai para senior-engineer em Opus)
- OWNERSHIP: arquivos e diretórios que esta task pode criar ou modificar
- dependências (IDs)
- testes necessários
- riscos
- classificação: PODE RODAR EM PARALELO / PRECISA AGUARDAR <ID> / BLOQUEIA <ID>

Monte o grafo de dependências.

Ordene os epics para maximizar trabalho independente em paralelo sem criar conflitos de edição nem dependências artificiais. Fundação (banco, auth, RBAC, contratos de API) vem antes de tudo que depende dela.

Duas tasks paralelas nunca compartilham ownership de arquivo. Se compartilham, uma depende da outra ou o arquivo é dividido.

Toda task tem pelo menos um AC. Task sem AC não entra.

Salve em docs/BACKLOG.md. Se o projeto tem cartão no Trello, sincronize a checklist de epics conforme a norma global.
```

**Formato de saída esperado:**

```text
EPIC 01 · FUNDAÇÃO
  E-1-T001  Schema inicial e migrations          backend   own: db/, prisma/      AC-01,AC-02   PARALELO
  E-1-T002  Autenticação                          backend   own: src/auth/         AC-03         AGUARDA T001
  E-1-T003  RBAC                                  backend   own: src/rbac/         AC-04         AGUARDA T002
  E-1-T004  Layout base e roteamento              frontend  own: src/app/, src/ui/ AC-05         PARALELO

EPIC 02 · CLIENTES
  ...
```

**DoD:** nenhuma task sem AC, sem ownership ou sem classificação de paralelismo. Nenhum par de tasks paralelas com ownership sobreposto.

---

### 09. IMPLEMENTAÇÃO

**Responsável:** Claude Lead + Agent Team.

Aqui começa o modelo multiagente. Você não microgerencia. O Lead distribui.

**Prompt padrão para uma Epic:**

```text
Implemente a EPIC <ID> inteira, task por task, conforme:
- CLAUDE.md
- documentação oficial em docs/
- arquitetura aprovada
- docs/BACKLOG.md (respeitando ownership e dependências)
- critérios de aceite
- nosso workflow global
- normas de engenharia do processo de início de projeto (KISS, YAGNI, sem comentários explicativos, sem código morto, tipos nas bordas, idempotência)

Atue como Lead e use Agent Team quando houver paralelização útil. Distribua entre os especialistas globais adequados. Cada agente recebe o ownership da task e não toca fora dele.

Antes de qualquer typecheck, build ou suíte pesada, respeite o teto global de processos da máquina. O Lead roda uma vez e distribui o resultado; subagentes não disparam por conta própria.

Execute a implementação completa da Epic.

Para aplicações web, frontend e QA validam os fluxos no produto renderizado com Playwright, não apenas lendo código.

Não considere a Epic concluída quando a implementação terminar. Após a implementação, execute automaticamente:
1. QA funcional
2. Security Review
3. Final Review
4. consolidação dos findings
5. correções pelos agentes donos dos módulos
6. regressão
7. novo QA/Security quando necessário
8. testes automatizados
9. lint e typecheck quando aplicável
10. build de produção

Continue o ciclo correção → regressão até não existirem problemas Critical/High nem bugs bloqueadores.

Ao final, apresente:
- o que foi implementado (por task, com AC cobertos)
- comandos de teste executados e resultado real
- findings encontrados e corrigidos
- riscos ou pendências restantes
- status final da Epic

Não faça deploy em produção sem minha autorização.
```

**Prompt reduzido para uma Task:**

```text
Implemente a TASK <ID> do BACKLOG.md conforme documentação, arquitetura, critérios de aceite, normas de engenharia e nosso workflow global.

Atue como Lead. Use os agentes globais necessários e paralelize o que for independente, respeitando ownership.

Não pare na implementação: execute QA, Security/Review quando aplicável, correções e regressão até a task estar realmente concluída.

Para funcionalidades web, valide o comportamento real com Playwright.

Não faça deploy em produção.
```

**Variante com limite de modelo/esforço para subagentes** (quando quiser economizar):

```text
[...] Para os subagentes de implementação use esforço low/medium. Esforço alto e o modelo mais forte ficam reservados ao Lead e aos revisores.
```

**DoD da Epic:** todos os ACs da epic verificados por QA (não pelo implementador). Zero Critical/High aberto. Suíte, lint, typecheck e build verdes. BACKLOG.md marcado. Trello sincronizado quando existir.

---

### 10. VERIFICAÇÃO INDEPENDENTE

**Responsável:** qa-engineer, security-reviewer, final-reviewer, em paralelo.

Seu global já dispara isso após implementação. Se precisar iniciar manualmente:

```text
A implementação desta etapa terminou.

Inicie a verificação independente conforme nosso workflow global. Rode em paralelo:

qa-engineer       valida comportamento real e cada critério de aceite; fluxos principais, de erro, bordas, papéis, responsivo quando web
security-reviewer audita auth, autorização por posse, IDOR, injeção, XSS, CSRF, segredos, webhooks, uploads, logs
final-reviewer    compara requisitos, arquitetura e implementação; procura o catálogo de falhas típicas de IA do processo (invenção, simplificação silenciosa, excesso, inconsistência, relato otimista)

Nesta primeira passada, os revisores REPORTAM findings ao Lead com severidade, arquivo:linha e cenário de falha. Não modificam código de outro dono.
```

---

### 11. CORREÇÕES

**Responsável:** Lead roteia, agentes donos corrigem.

```text
Consolide todos os findings de QA, Security e Final Review.

Classifique por severidade e impacto. Deduplique. Associe cada finding ao agente/módulo dono.

Distribua as correções aos respectivos implementadores. Prioridade:
1. Critical
2. High
3. bugs funcionais
4. regressões
5. Medium
6. Low

Toda correção de bug entra com um teste que falhava antes e passa depois.

Não considere um finding resolvido porque o código foi alterado. Resolvido é retestado.

Depois das correções, avance automaticamente para regressão.
```

---

### 12. REGRESSÃO

**Responsável:** QA + Security.

```text
Todas as correções desta rodada foram implementadas.

Execute regressão independente.

QA repete: cenários que falharam, fluxos diretamente afetados, principais fluxos adjacentes, critérios de aceite da Epic.

Security verifica novamente cada finding de segurança corrigido.

Execute os testes automatizados relevantes.

Se surgirem novos problemas, volte automaticamente para correção. Continue finding → correção → regressão até não restarem Critical/High nem bugs bloqueadores.
```

---

### 13. RELEASE CANDIDATE

**Responsável:** Claude. Ainda sem publicar.

```text
Prepare uma Release Candidate desta etapa.

Não faça deploy em produção.

Respeitando o teto global de processos da máquina, execute tudo que for aplicável:
- testes unitários, integração, E2E
- lint
- typecheck
- build de produção
- migration check (migrations pendentes, ordem, reversibilidade)
- validação de configuração e variáveis obrigatórias (nomes, não valores)
- análise de logs de desenvolvimento
- auditoria de dependências (vulnerabilidades conhecidas)
- confirmação dos critérios de aceite

Apresente relatório final com as seções:
IMPLEMENTADO · TESTADO · QA · SECURITY · BUILD · MIGRATIONS · RISCOS CONHECIDOS · PENDÊNCIAS · STATUS PARA RELEASE

Retorne READY FOR DEPLOY somente se realmente estiver apto. Caso contrário, NOT READY com a lista do que falta.

Não publique até minha autorização.
```

---

### 14. APROVAÇÃO DE DEPLOY · GATE HUMANO

**Responsável:** você.

Você trabalha com servidores e bancos reais. Este gate nunca é automatizado.

```text
Release aprovada.

Pode executar o deploy em produção conforme o procedimento documentado no RUNBOOK.

Após o deploy, execute smoke test e valide logs.
```

---

### 15. DEPLOY + SMOKE TEST

**Responsável:** Claude.

```text
Execute o deploy aprovado conforme docs/RUNBOOK.md.

Antes de qualquer comando que toque banco ou serviço, confirme explicitamente qual ambiente e qual banco.

Após a publicação:
1. confirme que os serviços subiram
2. valide migrations aplicadas
3. verifique logs
4. execute smoke tests dos fluxos críticos
5. valide autenticação
6. valide conectividade com banco
7. confirme APIs e integrações relevantes
8. confirme ausência de erros críticos de runtime

Se houver falha relevante: interrompa e reporte. Não execute rollback nem ação destrutiva sem autorização.
```

---

### 16. DOCUMENTAÇÃO FINAL

**Responsável:** Claude.

Essencial para você administrar vários sistemas depois.

```text
Com o deploy validado, finalize a documentação do projeto.

Atualize para refletir EXATAMENTE o estado atual da implementação:
PRODUCT, REQUIREMENTS, FLOWS, DATA-MODEL, ARCHITECTURE, ACCEPTANCE, DECISIONS, BACKLOG, CLAUDE.md

Crie ou atualize:
docs/RUNBOOK.md    iniciar, parar, reiniciar, build, deploy, migrations, backup, restauração, logs, serviços, variáveis (nomes), troubleshooting, health checks
docs/CHANGELOG.md  o que foi entregue nesta versão

Marque no backlog as tarefas realmente concluídas. Registre pendências reais para versões futuras.

Não documente como existente nada que não esteja implementado e testado.
```

**DoD:** alguém que nunca viu o projeto consegue subir, derrubar e diagnosticar o sistema só com o RUNBOOK.

---

## 6. Perfis: quanto do fluxo usar

O método é fixo. O Lead aplica somente as etapas necessárias para o tamanho da mudança.

| Situação | Etapas | Gates humanos |
|---|---|---|
| Projeto novo | 00 → 16 completo | 04, 05, 14 |
| Nova epic em sistema documentado | 08 → 16 (04/05 só se houver decisão de negócio ou mudança arquitetural) | 14 |
| Task isolada | 09 → 12, depois 13 quando fechar a release | 14 |
| Bug | análise → implementação com teste de regressão → QA → regressão | nenhum, salvo hotfix em produção (14) |
| Ajuste visual pequeno | implementação → verificação (Playwright) | nenhum |
| Mudança de regra de negócio | 04 (registrar em DECISIONS) → 06 → 08 → 09… | 04, 14 |
| Troca de stack ou infra | 05 → 06 → 07 → 08 → 09… | 05, 14 |

Regra de bolso: **se a mudança altera DECISIONS.md ou ARCHITECTURE.md, há gate humano. Se altera só código, não há.**

---

## 6.1 Modelos por papel

| Papel | Modelo | Motivo |
|---|---|---|
| Lead (sessão principal) | Fable | Orquestra, decide, escreve prompts fechados |
| backend-engineer, frontend-engineer | Sonnet | Tarefa fechada com ownership; custo baixo |
| senior-engineer | Opus (esforço low) | Tasks de complexidade alta |
| qa-engineer | Sonnet + Playwright | Executa roteiro e reporta |
| security-reviewer, final-reviewer | Opus (esforço low) | Julgamento; Sonnet perde findings |

Prompt para modelo menor é fechado, não aberto: ID, AC com texto, ownership, docs, comandos permitidos, formato de retorno. O agente não redescobre o que o Lead já sabe.

---

## 7. Estrutura final de um projeto

```
/projeto
├── CLAUDE.md                    operacional, curto, referencia docs/
├── README.md                    nome, propósito, ponteiro para docs/
├── .env.example                 nomes de variáveis, nunca valores
├── .gitignore
├── docs/
│   ├── fontes/                  matéria-prima, intocável
│   ├── referencias/             prints, visuais, exemplos
│   ├── PRODUCT.md
│   ├── REQUIREMENTS.md          RF-xxx / RNF-xxx com fonte
│   ├── FLOWS.md
│   ├── DATA-MODEL.md
│   ├── ARCHITECTURE.md          "APROVADA em <data>"
│   ├── ACCEPTANCE.md            AC-xxx ligados a RF
│   ├── DECISIONS.md             decisões datadas + pendências
│   ├── BACKLOG.md               epics, tasks, ownership, dependências
│   ├── RUNBOOK.md               operação
│   └── CHANGELOG.md
└── src/ (ou equivalente da stack)
```

---

## 9. Ciclo perpétuo, ondas e Trello

Depois da fundação (00–08) o projeto vive em ciclos. Cada ciclo é uma etapa (`[E-X]`) do BACKLOG.md.

```
/proxima-etapa E-X      fecha a anterior, limpa, atualiza memória, calcula ondas, sincroniza Trello
/epic E-X onda 1        implementa a onda 1 (subagentes em paralelo) + verificação
/epic E-X onda 2        ...
/release-candidate      quando a etapa fecha uma release
(aprovação humana)      deploy
/docs-finais            docs, RUNBOOK, CHANGELOG
/proxima-etapa E-X+1    e recomeça
```

**Onda** = conjunto de tasks executáveis no mesmo turno por subagentes diferentes. Regras: dependências satisfeitas por ondas anteriores; `own` disjunto dentro da onda; máximo 4 tasks; `complexidade: alta` vai para `senior-engineer`; toda etapa termina com uma onda de verificação, e correções entram como onda `.5`.

**Trello** é o espelho operacional (a fonte da verdade continua em `docs/`). Board próprio por projeto, com coluna REGRAS que prevalece sobre este texto. Padrão:

| Coluna | Cartão | Quem escreve |
|---|---|---|
| ETAPAS | `[E-X] título // módulo`, descrição vazia, uma checklist com todas as tasks | `/backlog` cria; `/epic` marca |
| A FAZER | `[E-X] Onda N · resumo // módulo`, tasks na descrição, ordem = prioridade | `/proxima-etapa` cria e ordena |
| FEITOS | ondas concluídas | `/epic` move |
| TO-DO | `[TD-X] título // dd/mm`, descrição inicia `[dd/mm // hh:mm]`, uma checklist | `/proxima-etapa` e `/epic` (findings abertos) |
| RECURSOS | nunca editar | ninguém |

O ID do board fica na linha `Trello:` do CLAUDE.md do projeto. Checklist só é marcada com QA automático verde. Dúvida de nome ou coluna: perguntar, nunca presumir.

**Higiene por ciclo** (feita por `/proxima-etapa`): matar processos órfãos por PID, apagar só artefatos regeneráveis (`.next`, `dist`, `coverage`, caches), registrar `df -h` e `free -h`, gravar em memória o que não está no repo, marcar BACKLOG.md, registrar DECISIONS.md. Uma sessão nova por etapa; a anterior termina com `/handoff` se houver contexto a transferir.

---

## 10. Sinais de que o processo está sendo violado

Se você observar qualquer um destes, pare e volte à etapa correspondente:

- Código sendo escrito antes de "APROVADA" aparecer em ARCHITECTURE.md → voltar a 05.
- Agente perguntando decisão técnica rotineira → ele deveria decidir e registrar; corrija o prompt.
- Agente escolhendo comportamento de negócio sem registrar → voltar a 04.
- Dois agentes editando o mesmo arquivo → ownership do backlog está errado; voltar a 08.
- "Concluído" sem comando de teste e saída no relato → não está concluído; exigir 10 a 12.
- Typecheck ou build demorando mais de 5 minutos → máquina saturada; contar processos e `free -h` antes de qualquer coisa, nunca reexecutar.
- Finding marcado "resolvido" sem reteste → voltar a 12.
- Documento em docs/ descrevendo algo que o código não faz → voltar a 16.
- Onda com duas tasks no mesmo `own`, ou Trello divergindo do BACKLOG.md → rodar `/proxima-etapa` de novo.

---

*Este documento é revisado quando o processo falha. Quando uma falha nova aparecer, ela entra na seção 4 ou na seção 8, com data e contexto, antes de o próximo projeto começar.*
