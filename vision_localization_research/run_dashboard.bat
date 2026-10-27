@echo off
title Vision Localization Research - Results Dashboard
echo ======================================================================
echo    VISION LOCALIZATION RESEARCH - Offline Evaluation Dashboard
echo ======================================================================
echo Launching Streamlit evaluation interface...
cd /d "%~dp0"
set "STREAMLIT=streamlit"
if exist ".venv\Scripts\streamlit.exe" set "STREAMLIT=.venv\Scripts\streamlit.exe"
%STREAMLIT% run src\vision_loc\dashboard_app.py --server.port 8502
pause
