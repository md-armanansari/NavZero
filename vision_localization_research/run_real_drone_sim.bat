@echo off
title Real Drone Autopilot & GPS-Jamming Mission Cockpit
cd /d "%~dp0"

echo ======================================================================
echo   AUTONOMOUS REAL-DRONE FLIGHT & GPS-JAMMING SIMULATOR
echo ======================================================================
echo.
echo Launching flight computer and visual telemetry loop...
echo.
echo CONTROLS:
echo   [J] = Toggle GPS Jamming ON / OFF
echo   [R] = Trigger Autonomous Visual Return-to-Home (V-RTH)
echo   [Q] = Exit simulator
echo.

.venv\Scripts\python.exe scripts\run_drone_sim.py

pause
