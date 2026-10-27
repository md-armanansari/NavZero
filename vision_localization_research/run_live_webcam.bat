@echo off
title Live Physical Webcam Visual Matching Engine
cd /d "%~dp0"

echo ======================================================================
echo   LIVE PHYSICAL WEBCAM DEMO - GPS-DENIED VISUAL LOCALIZATION
echo ======================================================================
echo.
echo Starting OpenCV real-time visual tracker...
echo.
echo HOW TO TEST:
echo 1. Point webcam at any book, printed photo, or phone screen.
echo 2. Press 'S' on your keyboard to SNAP that as your Target Reference.
echo 3. Move the book/phone around - watch green RANSAC inliers track live!
echo 4. Press 'Q' or ESC in the camera window to exit.
echo.

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"

%PYTHON% scripts\run_live_webcam.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Script encountered an issue (Exit Code: %ERRORLEVEL%).
)

echo.
echo Demo finished. Press any key to close this window.
pause >nul
