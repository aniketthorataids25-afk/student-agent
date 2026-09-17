# Study Companion — Complete Website

## What this project contains
- `backend/` — FastAPI Python API plus the original `agents/` and `core/` folders from the supplied ZIP.
- `frontend/` — responsive HTML/CSS/JavaScript dashboard.
- `start_backend.bat` — Windows backend launcher.
- `start_backend.sh` — macOS/Linux backend launcher.

## Run it
1. Install Python 3.10+.
2. Open a terminal in this project and run:
   `cd backend`
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Start the API:
   `python -m uvicorn app:app --reload`
5. Open `frontend/index.html` in your browser.

The frontend calls `http://127.0.0.1:8000/api`.
If your browser blocks local file requests, run a simple frontend server from the project root:
`python -m http.server 5500`
Then open `http://127.0.0.1:5500/frontend/`.

## API
- GET `/api/health`
- GET `/api/demo`
- POST `/api/analyze`

POST body example:
{
  "subjects": {
    "Mathematics": {"scores": [82, 74, 65, 58]},
    "Physics": {"scores": [88, 90, 87, 91]}
  }
}
