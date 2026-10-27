#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -f "$DIR/.venv/bin/pytest" ]; then
    "$DIR/.venv/bin/pytest" -v
else
    python3 -m pytest -v
fi
