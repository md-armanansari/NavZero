#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PYTHON="$DIR/vision_localization_research/.venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi

"$PYTHON" "$DIR/generate_project_pdf.py"
"$PYTHON" "$DIR/generate_proposal_pdf.py"
"$PYTHON" "$DIR/generate_raunak_proposal.py"
