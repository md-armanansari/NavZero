@echo off
title Interactive Ladakh Drone Tracker - Click to Dispatch Anywhere
cd /d "%~dp0"

echo ======================================================================
echo   INTERACTIVE REAL-MAP DRONE DISPATCHER (LADAKH SECTOR)
echo   Proof of Real-Time Computer Vision (Zero Predefined Routes!)
echo ======================================================================
echo.
echo Loading your Ladakh terrain map...
echo.
echo HOW TO TEST:
echo   - CLICK ANYWHERE ON THE MAP with your mouse (e.g. Kargil, Zanskar, Hanle).
echo   - The drone instantly jumps there and camera locks new ground features!
echo   - Press [J] = Toggle GPS Jamming ON / OFF
echo   - Press [R] = Trigger Autonomous Return-to-Home (V-RTH)
echo   - Press [Q] = Exit
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
%PYTHON% scripts\run_interactive_map_tracker.py

pause
