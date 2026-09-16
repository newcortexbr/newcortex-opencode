#!/bin/sh
# Install the pinned MarkItDown package in a project-local Python venv.
set -eu

BASE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
VERSION=0.1.6
TOOLS_DIR="$BASE_DIR/.opencode-local/tools/markitdown-$VERSION"
VENV="$TOOLS_DIR/venv"
PYTHON=${PYTHON:-python3}

command -v "$PYTHON" >/dev/null 2>&1 || {
  printf '%s\n' "MarkItDown install blocked: Python executable not found: $PYTHON" >&2
  exit 2
}

mkdir -p "$TOOLS_DIR"
if [ ! -x "$VENV/bin/python" ]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install \
  --disable-pip-version-check --no-input --no-cache-dir --only-binary=:all: \
  --requirement "$BASE_DIR/scripts/markitdown-requirements.txt"
"$VENV/bin/python" -c 'import importlib.metadata; assert importlib.metadata.version("markitdown") == "0.1.6"'
"$VENV/bin/python" -c 'from markitdown import MarkItDown; MarkItDown(enable_plugins=False)'
"$VENV/bin/python" -m markitdown --version
