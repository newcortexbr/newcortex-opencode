#!/usr/bin/env python3
"""Convert one explicitly named local file with built-in converters only."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

# ONNX Runtime reads this setting when its dependency graph is initialized.
os.environ["ORT_DISABLE_TELEMETRY"] = "1"

from markitdown import MarkItDown


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert one local file to Markdown; URLs, stdin, and plugins are disabled."
    )
    parser.add_argument("path", help="path to an existing regular local file")
    args = parser.parse_args()

    raw_path = args.path
    if raw_path.startswith(("http:", "https:", "file:", "data:")) or "://" in raw_path:
        parser.error("URI input is blocked; provide a local file path")

    path = Path(raw_path)
    if not path.is_file():
        parser.error(f"local regular file not found: {raw_path}")

    result = MarkItDown(enable_plugins=False).convert_local(path)
    sys.stdout.write(result.markdown)
    if result.markdown and not result.markdown.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
