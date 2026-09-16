#!/bin/sh
# Convert an explicitly named local file through the pinned venv.
set -eu

BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
VERSION=0.1.6
PYTHON="$BASE_DIR/.opencode-local/tools/markitdown-$VERSION/venv/bin/python"

if [ ! -x "$PYTHON" ]; then
  printf '%s\n' "MarkItDown is not installed: run $BASE_DIR/scripts/markitdown-install.sh" >&2
  exit 127
fi
if [ "$#" -ne 1 ]; then
  printf '%s\n' "usage: $0 <local-file>" >&2
  exit 2
fi

exec env PYTHONNOUSERSITE=1 ORT_DISABLE_TELEMETRY=1 "$PYTHON" "$BASE_DIR/scripts/markitdown-local.py" "$1"
