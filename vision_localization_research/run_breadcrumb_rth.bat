@echo off
title Scenario B - Autonomous Zero-Map Breadcrumb Return-To-Home
cd /d "%~dp0"

echo ======================================================================
echo   SCENARIO B: AUTONOMOUS ZERO-MAP BREADCRUMB RETURN-TO-HOME (V-RTH)
echo   100%% Zero Pre-Loaded Map Navigation
echo ======================================================================
echo.
echo Initializing camera and establishing Home Base (Frame 0)...
echo.
echo CONTROLS:
echo   [J] = Toggle GPS Jamming ON / OFF
echo   [R] = Trigger Emergency Visual Return-to-Home (V-RTH)
echo   [Q] = Exit
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
%PYTHON% scripts\run_breadcrumb_rth.py

pause
