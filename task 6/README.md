# Task 6 - Face Profiling

This project implements:

- **FastAPI backend** for facial landmark detection and feature measurement (eyes, nose, mouth, jawline)
- **Flask frontend** for image upload and result visualization
- Heuristic **MBTI (16 Personality Types)** mapping from measured facial feature ratios

## Project structure

- `backend/main.py` - FastAPI app (`/health`, `/analyze`)
- `backend/face_profiler.py` - dlib/OpenCV landmark measurement logic
- `backend/personality.py` - MBTI heuristic mapper
- `frontend/app.py` - Flask UI app
- `frontend/templates/index.html` - upload/result page

## Requirements

- Python 3.10+
- CMake build tools (needed by dlib on some Windows systems)
- Visual C++ Build Tools (needed by dlib on Windows if wheel unavailable)

### Python 3.14 note

- `dlib` currently may fail to build on Python 3.14 in some Windows setups.
- This project automatically falls back to OpenCV cascade-based feature estimation when dlib/model is unavailable.
- For full dlib 68-landmark precision, use Python 3.10-3.13 with CMake + VS Build Tools.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Download dlib landmark model

```powershell
python -m backend.face_profiler --download-model
```

This downloads `shape_predictor_68_face_landmarks.dat` into `backend/models/`.
If this model is missing, the API still works using OpenCV fallback mode.

## Run FastAPI backend

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Flask frontend

Open a second terminal:

```powershell
python frontend/app.py
```

Then open: `http://127.0.0.1:5000`

## API usage

### Health

- `GET /health`

### Analyze image

- `POST /analyze`
- form-data field: `image` (file)

Example with curl:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" -F "image=@face.jpg"
```

## Notes

- MBTI output is a rough demo heuristic and **not** a validated psychological assessment.
- If no face is found, API returns `422` with `No face detected`.
- Response contains `landmark_backend` to indicate whether `dlib_68` or `opencv_cascade_fallback` was used.
