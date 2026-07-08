#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[all smoke] project root: $ROOT_DIR"

for f in tools/smoke_*.js; do
  echo "[node] $f"
  node "$f"
done

for f in tools/smoke_*.py; do
  echo "[python] $f"
  python "$f"
done

echo "[all smoke] passed"
