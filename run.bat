@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv || exit /b 1
)

".venv\Scripts\python.exe" -c "import pygame" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1
)

".venv\Scripts\python.exe" gamepad_vibration.py
exit /b %errorlevel%