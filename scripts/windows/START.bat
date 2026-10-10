@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
title Minecraft World Dashboard
where python >nul 2>nul
if errorlevel 1 (
  echo You need Python. Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) and open this file again.
  pause
  exit /b 1
)
python start.py
pause
