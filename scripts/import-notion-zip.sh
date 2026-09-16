#!/bin/sh
# extrai zip exportado do Notion para o vault local (pasta fontes)
# uso: ./scripts/import-notion-zip.sh <arquivo.zip>
# nao requer token; nao acessa rede; nao envia dados; sem normalizacao automatica.
set -eu

if [ -z "${1:-}" ]; then
  printf '%s\n' 'uso: ./scripts/import-notion-zip.sh <arquivo.zip>' >&2
  exit 1
fi

zipfile="$1"
if [ ! -f "$zipfile" ]; then
  printf '%s\n' "arquivo nao encontrado: $zipfile" >&2
  exit 1
fi

dest="vault/fontes"
mkdir -p "$dest"

printf '%s\n' "extraindo $zipfile em $dest ..."
unzip -o -d "$dest" "$zipfile"

printf '%s\n' "conteudo importado em $dest (sem normalizacao automatica). revise manualmente se necessario."
