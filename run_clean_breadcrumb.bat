@echo off
title Scenario B - Clean Teach and Repeat Visual Breadcrumbs (V-RTH)
echo ======================================================================
echo   PROJECT NAVZERO - SCENARIO B: CLEAN TEACH-AND-REPEAT RETURN-TO-HOME
echo   Phase 1: Record Trail Quietly -^> Phase 2: Compare in Reverse on Return
echo ======================================================================
echo.
cd /d "%~dp0\vision_localization_research"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe scripts\run_clean_breadcrumb_rth.py
) else (
    python scripts\run_clean_breadcrumb_rth.py
)
pause
