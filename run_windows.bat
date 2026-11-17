@echo off
cd /d %~dp0
py -m pip install -r requirements.txt
py -m http.server 8080 --directory frontend
