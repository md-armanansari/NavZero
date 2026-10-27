@echo off
setlocal
cd /d "%~dp0"
title NavZero Ladakh Tactical Waypoint Dispatcher
color 0E

echo ==========================================================================
echo   LAUNCHING LADAKH POINT-AND-CLICK MISSION WAYPOINT DISPATCHER
echo ==========================================================================
echo.
echo HOW TO CONTROL:
echo   - RIGHT-CLICK : Set Home Base runway address
echo   - LEFT-CLICK  : Add tactical mission waypoints (WP-1, WP-2, WP-3...)
echo   - [C] Key     : Clear current flight plan
echo   - [R] Key     : Visual Return-to-Home (RTH)
echo   - [J] Key     : Inject Electronic Warfare GPS Jamming
echo   - [Q] Key     : Quit
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
if exist "vision_localization_research\.venv\Scripts\python.exe" set "PYTHON=vision_localization_research\.venv\Scripts\python.exe"

"%PYTHON%" vision_localization_research\scripts\run_tactical_mission_dispatcher.py
pause
