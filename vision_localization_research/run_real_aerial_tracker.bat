@echo off
title Real Aerial Flight Tracker - 100%% Photographic Terrain
cd /d "%~dp0"

echo ======================================================================
echo   REAL AERIAL FLIGHT LOCALIZATION TRACKER
echo   Processing 100%% Real Photographic Pixels (Zero Synthetic Noise)
echo ======================================================================
echo.
echo Loading high-resolution real aerial orthophoto into OpenCV...
echo.
echo CONTROLS:
echo   [J] = Toggle GPS Jamming ON / OFF
echo   [R] = Trigger Autonomous Visual Return-to-Home (V-RTH)
echo   [Q] = Exit
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
%PYTHON% scripts\run_real_aerial_tracker.py

pause
