@echo off
title NavZero Tactical Ground Control Station
echo ==========================================================
echo    NavZero: Autonomous Optical GPS-Denied Navigation
echo    Atmanirbhar Bharat Indigenous Defence Software
echo ==========================================================
echo Starting Tactical Ground Control Station Dashboard...
cd /d "%~dp0"
python -m streamlit run app.py
pause
