#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <path-to-ebook.pdf|.epub> [--model MODEL] [--prompt ALIAS]" >&2
  exit 1
fi

python -m src.cli.pipeline_cli "$@"

