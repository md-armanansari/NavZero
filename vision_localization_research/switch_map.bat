@echo off
title Switch Terrain Map (Ladakh vs Ocean Stress Test)
cd /d "%~dp0"

.venv\Scripts\python.exe scripts\switch_terrain_map.py

pause
