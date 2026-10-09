@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Minecraft World Dashboard
where python >nul 2>nul
if errorlevel 1 (
  echo Necesitas Python. Instalalo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH" y vuelve a abrir este archivo.
  pause
  exit /b 1
)
python start.py
pause
