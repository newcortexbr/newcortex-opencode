# capacidades locais · E3

status: instalacao local e testes sinteticos reportados na rodada de 2026-09-13.
Este registro descreve apenas os wrappers e binarios locais desta rodada; nao
altera o launcher, `v2/` ou os contratos do core. A validacao central da rodada
foi repetida para as correções: 5 testes sintéticos MarkItDown OK; limites abaixo.

## alcance e ownership

- RTK e MarkItDown foram baixados/instalados somente em `.opencode-local/tools/`.
- Os wrappers autorizados sao `scripts/rtk-*` e `scripts/markitdown-*`.
- Nao foi instalado hook, plugin MarkItDown, servidor HTTP, MCP, Exa ou servico
  externo adicional.
- A instalacao local e uma conveniencia de processo; nao e sandbox de processo.

## fontes e versoes fixadas

As consultas Context7 foram feitas primeiro usando as fontes oficiais:

- RTK: `/rtk-ai/rtk`; configuracao e telemetria em
  `https://github.com/rtk-ai/rtk/blob/v0.49.0/docs/guide/getting-started/configuration.md`
  e `https://github.com/rtk-ai/rtk/blob/v0.49.0/docs/TELEMETRY.md`.
- RTK release: `https://github.com/rtk-ai/rtk/releases/tag/v0.49.0`.
  Asset Linux x86_64: `rtk-x86_64-unknown-linux-musl.tar.gz`.
  SHA-256 verificado: `7278231dfd7e6a730a4ab7f847b195bcf02289c2d57622b0dab75a6411100c8f`.
- MarkItDown: `/microsoft/markitdown`; README em
  `https://github.com/microsoft/markitdown/tree/v0.1.6` e API local em
  `https://github.com/microsoft/markitdown/blob/v0.1.6/packages/markitdown/src/markitdown/_markitdown.py`.
- MarkItDown PyPI: `https://pypi.org/project/markitdown/0.1.6/`; pacote fixado
  em `0.1.6`, com dependencias exatas registradas em
  `scripts/markitdown-requirements.txt`.

## RTK

Instalacao e execucao:

```text
./scripts/rtk-install.sh
./scripts/rtk-local.sh <comando-rtk> [args...]
./scripts/bin/rtk <comando-rtk> [args...]
```

O instalador aceita apenas Linux `x86_64` ou `aarch64` com asset prebuilt
publico, verifica SHA-256 e nao compila nem usa `sudo`. O wrapper aponta `HOME`,
`XDG_CONFIG_HOME`, `XDG_DATA_HOME` e `XDG_CACHE_HOME` para o runtime local.

O primeiro argumento precisa ser um comando aprovado: `ls`, `tree`, `read`,
`smart`, `git`, `test`, `pytest`, `tsc`, `diff`, `log`, `grep`, `rg`, `wc` ou
`run`. `--version` e `--help` sao excecoes permitidas somente quando forem o
unico argumento. Qualquer `--config`, `--verbose`, `--skip-env`, `proxy`,
`telemetry`, hook ou outro comando fora da allowlist e rejeitado antes do
binario; nao ha parser que pule opcoes globais para encontrar um comando.

Politica efetiva observada em
`.opencode-local/tools/rtk-runtime/config/rtk/config.toml`:

- `tracking.enabled = false` e `retriever.mode = "disabled"`: sem historico,
  recall ou tee de saida integral.
- `telemetry.enabled = false`, `RTK_TELEMETRY_DISABLED=1`: sem telemetria.
- `RTK_RECALL=0`, `RTK_TEE=0`: kill switches por invocacao.
- nenhum `rtk init` foi executado: nao ha hook instalado.
- o wrapper exige que o arquivo exista, seja legivel e contenha explicitamente
  `enabled = false` sem `enabled = true`, alem de `mode = "disabled"`; ausencia
  ou config persistente falha antes de executar o binario.
- o processo e iniciado com `env -i` e somente PATH/runtime/politicas locais sao
  reinjetados; variaveis externas nao podem substituir config ou flags RTK.

Limite importante: comandos RTK filtrados podem elidir linhas. Como recall e
persistencia estao desativados, essa saida nao pode ser recuperada depois.
`rtk run` continua disponivel somente como chamada explicita para uma saida
bruta sem tracking; ele nao e uma prova de filtragem RTK.

`scripts/bin/rtk` e apenas um entrypoint local para o wrapper acima. Nao altera
`PATH`, instala globalmente ou promete sandbox para comandos filhos.

## MarkItDown

Instalacao e execucao:

```text
./scripts/markitdown-install.sh
./scripts/markitdown-local.sh <arquivo-local>
./scripts/bin/markitdown <arquivo-local>
```

O venv esta em `.opencode-local/tools/markitdown-0.1.6/venv`. O wrapper e o
script Python definem `ORT_DISABLE_TELEMETRY=1` antes de importar MarkItDown,
portanto antes de inicializar a cadeia de dependencias ONNX Runtime. O wrapper
chama `MarkItDown(enable_plugins=False).convert_local(path)`, exigindo um
arquivo regular local existente. Rejeita `http:`, `https:`, `file:`, `data:` e
entradas com `://`; nao aceita stdin, `--use-plugins`, endpoints Azure ou saida
remota. A conversao escreve Markdown em stdout para o chamador redirecionar
localmente.

Limite importante: MarkItDown executa com os privilegios do processo e a
conversao local nao constitui sandbox nem garantia de egress zero. Plugins estao
desativados e nenhum plugin esta instalado, mas essa configuracao nao bloqueia
syscalls/rede nem prova que nenhuma dependencia tente comunicar-se. o lead
inspecionou os dois entrypoints e repetiu os testes: ambiente ausente ou `0`
chega como `1` ao import sintético. não houve nova conversão real ou captura de rede.

## provas executadas

Comandos sinteticos pequenos executados com `0` typecheck/build concorrentes e
memoria disponivel acima de 3 GiB:

- `./scripts/rtk-install.sh`: `rtk 0.49.0`; checksum `OK`.
- `./scripts/rtk-local.sh --version`: `rtk 0.49.0`.
- config RTK presente foi validada pelo wrapper: tracking, retriever e telemetry
  explicitamente desativados; arquivo ausente ou persistente e rejeitado antes
  do binario.
- `./scripts/rtk-local.sh run -c 'printf "alpha\\nbeta\\n"'`: stdout integral
  esperado; `proxy`, `--config`, `--verbose proxy` e `--version extra` foram
  rejeitados pelo wrapper.
- `scripts/bin/rtk --version` delegou somente ao wrapper local.
- comando RTK com falha sintetica retornou status `7`; nenhum `history.db` ou
  `rtk.db` foi criado no runtime local.
- `./scripts/markitdown-install.sh`: `markitdown 0.1.6`; import de
  `MarkItDown(enable_plugins=False)` passou.
- `python -m markitdown --list-plugins`: `No 3rd-party plugins installed`.
- fixture Markdown local com `# Synthetic fixture` e `alpha beta` foi convertido
  e ambos os trechos apareceram no stdout.
- entrada `https://example.invalid/file.txt` foi rejeitada antes da conversao.
- `scripts/bin/markitdown` converteu fixture local e nao criou instalacao global.

Resultado reportado da rodada: RTK e MarkItDown estao instalados localmente e
os contratos do wrapper passaram nos testes sinteticos descritos acima. Isso
nao prova ausencia geral de telemetria/egress. a correção R-05 passou em 5 testes
centrais (`scripts/test_markitdown_local.py`) e `sh -n`, sem pacote real. ficam
pendentes testes de formatos binarios maiores e medicao comparativa de
perda/latencia; nenhum deles foi declarado nesta prova pequena.
