#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  GENERATING DEFENCE PROJECT & INCUBATION PROPOSAL PDFs"
echo "======================================================================"

PYTHON="$DIR/vision_localization_research/.venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi

"$PYTHON" "$DIR/generate_project_pdf.py"
"$PYTHON" "$DIR/generate_proposal_pdf.py"
"$PYTHON" "$DIR/generate_raunak_proposal.py"

echo ""
echo "All PDFs generated successfully in $DIR!"
echo ""
read -p "Press Enter to exit..."
