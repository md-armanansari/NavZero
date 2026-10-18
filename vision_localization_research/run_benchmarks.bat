@echo off
title Vision Localization Research - Benchmark Runner
echo ======================================================================
echo    VISION LOCALIZATION RESEARCH - Automated Benchmark Runner
echo ======================================================================
echo Executing benchmark pipeline with unrecorded warmup and 5 steady-state passes...
cd /d "%~dp0"
.\.venv\Scripts\python.exe scripts\run_benchmarks.py
pause
