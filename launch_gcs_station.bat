@echo off
setlocal
cd /d "%~dp0"
title NavZero Tactical Ground Control Station (GCS)
color 0A

echo ==========================================================================
echo   LAUNCHING NAVZERO TACTICAL GROUND CONTROL STATION (STANAG-4586)
echo ==========================================================================
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
if exist "vision_localization_research\.venv\Scripts\python.exe" set "PYTHON=vision_localization_research\.venv\Scripts\python.exe"

echo Starting Streamlit GCS Server on http://localhost:8501 ...
"%PYTHON%" -m streamlit run navzero/app.py --server.headless=false --theme.base="dark"
pause
