@echo off
title Vision Localization Research - Results Dashboard
echo ======================================================================
echo    VISION LOCALIZATION RESEARCH - Offline Evaluation Dashboard
echo ======================================================================
echo Launching Streamlit evaluation interface...
cd /d "%~dp0"
.\.venv\Scripts\streamlit.exe run src\vision_loc\dashboard_app.py --server.port 8502
pause
