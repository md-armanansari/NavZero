@echo off
title Switch Terrain Map (Ladakh vs Ocean Stress Test)
cd /d "%~dp0"

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PYTHON=.venv\Scripts\python.exe"
%PYTHON% scripts\switch_terrain_map.py

pause
