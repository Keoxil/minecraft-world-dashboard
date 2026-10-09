@echo off
rem Sirve la pagina en local y abre un tunel de Cloudflare para compartirla (hace falta tener cloudflared instalado).
cd /d "%~dp0..\.."
where cloudflared >nul 2>nul
if errorlevel 1 (
  echo No encuentro cloudflared. Descargalo de https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
  pause
  exit /b 1
)
set "PORT=%MCDASH_PORT%"
if not defined PORT set "PORT=8765"
start "" /b pythonw serve.py
timeout /t 2 /nobreak >nul
echo Cierra esta ventana para dejar de compartir.
cloudflared tunnel --no-autoupdate --url http://127.0.0.1:%PORT%
