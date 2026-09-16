# arquitetura do vault obsidian · opencode prefs v2

status: desenho aprovado em D-022; protocolo exercitado por agente Terra
orquestrado em 2026-09-13. integração automática na V2 ainda não validada;
piloto de protocolo não equivale a entrega funcional completa.

## objetivo

biblioteca de conhecimento reutilizável, legível no obsidian e explorada
prioritariamente pelos agentes. docs do projeto continuam como verdade
específica; o vault guarda o que atravessa projetos.

## princípios operacionais

- fonte canônica: markdown puro, sem plugin obrigatório.
- uma nota = um assunto; curta; com título, data, origem, status.
- links explícitos; nenhuma relação inferida tratada como fato.
- leitura sob demanda via `00-index.md`; nunca carregar o vault inteiro.
- escrita automática pelos agentes: categorização, indexação, promoção,
  deduplicação e links. sem barreira humana obrigatória.
- sem auditoria periódica obrigatória; sem log obrigatório (pode ser ativado
  manualmente se necessário).
- sem segredos, credenciais, dados pessoais ou conteúdo privado.

## estrutura

```text
vault/
  00-index.md      → mapa curto; atualizado automaticamente
  conceitos/       → definições estáveis
  procedimentos/   → passo a passo comprovado
  projetos/        → contexto reutilizável, sem segredo
  fontes/          → resumo com link/autor/data, nunca cópia integral
  inbox/           → propostas dos agentes; promoção automática
```

## convenção de nota

cada nota contém:

- título curto;
- data;
- origem (projeto, conversa, url, experiência);
- status: `rascunho` | `válido` | `superado`;
- corpo breve (poucas linhas);
- links `[[nota]]` para notas relacionadas.

exemplo mínimo:

```markdown
# retomar sessão opencode no zed
- origem: opencode-prefs-v2, 2026-09-11
- status: válido
ver também: [[sessões acp e zed]]
```

## protocolo de leitura (agentes)

1. ler `00-index.md`;
2. buscar por palavra-chave no índice e títulos;
3. ler só as notas pertinentes (máximo 2–3 por vez);
4. citar nota usada; se não achar, informar que não achou.

## protocolo de escrita (agentes — automático)

1. decidir pasta (`conceitos/`, `procedimentos/`, etc.);
2. criar ou atualizar nota com cabeçalho padrão e links;
3. atualizar `00-index.md` na seção correspondente;
4. detectar sobreposição/conflito: fundir, marcar `superado` ou criar
   nova versão; não duplicar assunto sem razão;
5. respeitar restrições: sem segredos, sem cópia integral sem link,
   sem conteúdo privado.

nenhuma verificação manual obrigatória antes de promover de `inbox/`.

## localização e versionamento

- local: `vault/` dentro do repositório do projeto.
- persistência: versionado no GitHub junto ao projeto; backup por push.
- sincronização: não depende de cliente de sync proprietário; qualquer
  ferramenta que leia/escreva arquivos Markdown funciona.

## obsidian

o vault é uma pasta de Markdown; o obsidian reflete edições externas
automaticamente. links `[[nota]]` funcionam no obsidian e continuam legíveis
como texto puro fora dele. nenhum plugin obrigatório.

## graphify (opcional, futuro)

se busca textual falhar num caso documentado, testado com evidência:

- construir grafo derivado a partir do vault existente;
- consultar e comparar com busca textual simples;
- nunca tratar relação `INFERRED` como nota canônica sem revisão.
- exportação para vault só se não poluir a biblioteca; reconstruível.

não ativar automaticamente; só após validação observável.

## aceitação do piloto

- [x] estrutura criada (`vault/` + `00-index.md` + pastas).
- [x] agente recupera nota correta em 3 consultas sem carregar tudo (Terra
  orquestrado: uma nota selecionada pelo índice por consulta).
- [x] agente cria/atualiza nota, índice e links automaticamente (piloto orquestrado).
- [x] promoção de `inbox/` sem aprovação intermediária demonstrada com evidência
  sintética: original preservado como `superado`, procedimento novo indexado.
- [x] desenho registrado em `DECISIONS.md` (D-022).
- [x] evidências do piloto de protocolo registradas no backlog após validação.
- [ ] repetir aceites na configuração viva V2; provar integração de escrita,
  promoção e tratamento de sobreposição em tarefa real. o detector local só
  identifica duplicatas, não executa fusão automática.
