@echo off
title Tactical Mission Dispatcher - Fly To Target and Return Home
cd /d "%~dp0"

echo ======================================================================
echo   TACTICAL MISSION DISPATCHER & VISUAL WAYPOINT NAVIGATOR
echo ======================================================================
echo.
echo HOW TO TEST:
echo   1. RIGHT-CLICK on the map to set HOME BASE (e.g. your runway).
echo   2. LEFT-CLICK on the map to set MISSION TARGET.
echo      -> Drone flies autonomously to target, matching terrain at 30 FPS!
echo   3. Press [R] at ANY TIME to CALL THE DRONE BACK to Home Base!
echo   4. Press [J] = Toggle GPS Jamming ON / OFF
echo   5. Press [Q] = Exit
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
%PYTHON% scripts\run_tactical_mission_dispatcher.py

pause
