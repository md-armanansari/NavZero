@echo off
echo ===============================================================================
echo                NAVZERO DEFENSE COMBAT EVALUATION BENCHMARK
echo        Autonomous GNSS-Denied Optical Relocalization Test Runner
echo ===============================================================================
echo.

python "%~dp0vision_localization_research\scripts\run_defense_benchmark.py" --steps 30

echo.
echo ===============================================================================
echo Benchmark trial complete. Results exported to vision_localization_research\data\
echo ===============================================================================
pause
