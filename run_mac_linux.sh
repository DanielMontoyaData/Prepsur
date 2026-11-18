#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
[ -f frontend/vendor/leaflet/leaflet.js ] || echo "Falta frontend/vendor. Ejecuta: npm install && npm run sync:vendor"
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
API=$!; trap 'kill $API 2>/dev/null' EXIT
python3 -m http.server 8080 --directory frontend
