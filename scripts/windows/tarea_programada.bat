@echo off
rem Crea una tarea programada que ejecuta build.py cada minuto, sin abrir ninguna ventana.
for %%I in ("%~dp0..\..") do set "ROOT=%%~fI"
set "PYW="
for /f "delims=" %%P in ('where pythonw 2^>nul') do if not defined PYW set "PYW=%%P"
if not defined PYW (
  echo No encuentro pythonw.exe. Instala Python desde python.org y marca "Add python.exe to PATH".
  pause
  exit /b 1
)
schtasks /Create /TN "MinecraftWorldDashboard" /SC MINUTE /MO 1 /F /TR "\"%PYW%\" \"%ROOT%\build.py\""
if errorlevel 1 (echo No se pudo crear la tarea.) else (echo Tarea creada: build.py se ejecutara cada minuto.)
pause
