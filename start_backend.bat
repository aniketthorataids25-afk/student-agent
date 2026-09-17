@echo off
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
