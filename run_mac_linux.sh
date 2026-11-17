#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m http.server 8080 --directory frontend
