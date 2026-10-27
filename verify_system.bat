@echo off
title NavZero // Master System & Module Integrity Verifier
echo ===============================================================================
echo                NAVZERO MASTER SYSTEM & MODULE INTEGRITY VERIFIER
echo           Autonomous GPS-Denied Optical Guidance Verification Suite
echo ===============================================================================
echo.

python "%~dp0verify_all_modules.py"

echo.
echo ===============================================================================
echo Verification complete. Press any key to exit.
echo ===============================================================================
pause >nul
