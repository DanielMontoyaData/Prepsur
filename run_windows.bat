@echo off
cd /d %~dp0
py -m pip install -r requirements.txt
if not exist frontend\vendor\leaflet\leaflet.js (
  echo Falta frontend\vendor. Ejecuta: npm install ^&^& npm run sync:vendor
)
rem API privada en 127.0.0.1:8000 (requiere PREPPER_TOKENS en el entorno)
start "PREPPER MAP API" py -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
rem Interfaz web local
start "" http://localhost:8080
py -m http.server 8080 --directory frontend
