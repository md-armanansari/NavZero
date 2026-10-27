@echo off
setlocal enabledelayedexpansion
title NavZero: Autonomous Vision-Based GPS-Denied Drone Navigation
cd /d "%~dp0"

:: Auto-detect Python interpreter
set "PYTHON=python"
if exist "%~dp0vision_localization_research\.venv\Scripts\python.exe" (
    set "PYTHON=%~dp0vision_localization_research\.venv\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON=%~dp0.venv\Scripts\python.exe"
)

:MENU
cls
echo ==========================================================================
echo      NAVZERO: AUTONOMOUS GPS-DENIED OPTICAL DRONE NAVIGATION
echo      Atmanirbhar Bharat Indigenous Defence Software (Windows Launcher)
echo ==========================================================================
echo.
echo   WEB GROUND STATIONS ^& EVALUATION DASHBOARDS:
echo     [1] NavZero Tactical Ground Control Station (Streamlit Web App)
echo     [2] Research Evaluation Dashboard (Streamlit Web App)
echo.
echo   TACTICAL FLIGHT COCKPIT ^& TERRAIN SIMULATORS (OpenCV GUI):
echo     [3] Real Drone Autopilot ^& GPS-Jamming Cockpit Simulator
echo     [4] Interactive Ladakh Drone Dispatcher (Click to fly anywhere)
echo     [5] Tactical Mission Waypoint Navigator (Set Home Base ^& Target)
echo     [6] Zero-Map Breadcrumb Return-to-Home (V-RTH)
echo     [7] Real Aerial Flight 100%% Photographic Terrain Tracker
echo     [8] Live Physical Webcam Visual Matching Engine
echo.
echo   TOOLS, BENCHMARKS ^& TESTS:
echo     [9] Switch Active Terrain Map (Ladakh / CU Campus / Farmland / Ocean)
echo    [10] Run Benchmark Suite (7 trials + CSV + diagnostic plots)
echo    [11] Run All Automated Unit ^& Integration Tests (pytest)
echo.
echo     [Q] Quit
echo ==========================================================================
set "choice="
set /p "choice=Select option [1-11 or Q]: "

if not defined choice (
    echo.
    echo Please enter a number from 1 to 11, or Q to quit.
    timeout /t 2 >nul
    goto MENU
)

:: Strip any surrounding quotes or spaces
set "choice=!choice:"=!"
set "choice=!choice: =!"

if /i "!choice!"=="1" goto OP1
if /i "!choice!"=="2" goto OP2
if /i "!choice!"=="3" goto OP3
if /i "!choice!"=="4" goto OP4
if /i "!choice!"=="5" goto OP5
if /i "!choice!"=="6" goto OP6
if /i "!choice!"=="7" goto OP7
if /i "!choice!"=="8" goto OP8
if /i "!choice!"=="9" goto OP9
if /i "!choice!"=="10" goto OP10
if /i "!choice!"=="11" goto OP11
if /i "!choice!"=="q" goto END
if /i "!choice!"=="quit" goto END
if /i "!choice!"=="exit" goto END

echo.
echo [!] Invalid option "!choice!". Please type a number between 1 and 12, or Q to quit.
echo.
pause
goto MENU

:OP1
echo.
echo ==========================================================================
echo >>> Launching NavZero Tactical Ground Control Station on http://localhost:8501 ...
echo ==========================================================================
cd /d "%~dp0navzero"
%PYTHON% -m streamlit run app.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP2
echo.
echo ==========================================================================
echo >>> Launching Research Evaluation Dashboard on http://localhost:8502 ...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% -m streamlit run src/vision_loc/dashboard_app.py --server.port 8502
cd /d "%~dp0"
echo.
pause
goto MENU

:OP3
echo.
echo ==========================================================================
echo >>> Launching Real Drone Autopilot ^& Cockpit Simulator...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_drone_sim.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP4
echo.
echo ==========================================================================
echo >>> Launching Interactive Ladakh Drone Dispatcher...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_interactive_map_tracker.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP5
echo.
echo ==========================================================================
echo >>> Launching Tactical Mission Waypoint Navigator...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_tactical_mission_dispatcher.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP6
echo.
echo ==========================================================================
echo >>> Launching Zero-Map Breadcrumb Return-to-Home...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_breadcrumb_rth.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP7
echo.
echo ==========================================================================
echo >>> Launching Real Aerial Flight 100%% Photographic Terrain Tracker...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_real_aerial_tracker.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP8
echo.
echo ==========================================================================
echo >>> Launching Live Physical Webcam Visual Matching Engine...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_live_webcam.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP9
echo.
echo ==========================================================================
echo >>> Switching Terrain Map...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\switch_terrain_map.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP10
echo.
echo ==========================================================================
echo >>> Running Benchmark Suite...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% scripts\run_benchmarks.py
cd /d "%~dp0"
echo.
pause
goto MENU

:OP11
echo.
echo ==========================================================================
echo >>> Running Automated Unit Tests...
echo ==========================================================================
cd /d "%~dp0vision_localization_research"
%PYTHON% -m pytest -v
cd /d "%~dp0"
echo.
pause
goto MENU

:END
echo Exiting NavZero launcher. Goodbye!
exit /b 0
