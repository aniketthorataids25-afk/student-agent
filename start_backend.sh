#!/bin/sh
cd "$(dirname "$0")/backend"
python3 -m pip install -r requirements.txt
python3 -m uvicorn app:app --reload
