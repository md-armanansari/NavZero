"""
Automated unit test for run_defense_benchmark CLI script.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_benchmark_execution():
    project_root = Path(__file__).resolve().parent.parent.parent
    script_path = project_root / "vision_localization_research" / "scripts" / "run_defense_benchmark.py"

    cmd = [sys.executable, str(script_path), "--steps", "3", "--scenario", "ALPHA_FORWARD_INGRESS"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root), timeout=30)

    assert res.returncode == 0
    assert "DEFENSE COMBAT EVALUATION MATRIX" in res.stdout
    assert "ALPHA_FORWARD_INGRESS" in res.stdout or "Operation Desert Falcon" in res.stdout
    assert "CEP95 ACCURACY" in res.stdout
