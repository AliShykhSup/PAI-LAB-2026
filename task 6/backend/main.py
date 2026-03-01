from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.face_profiler import FaceProfiler, ModelMissingError
from backend.personality import infer_mbti

app = FastAPI(title="Face Profiling API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_face(image: UploadFile = File(...)) -> dict:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    try:
        profiler = FaceProfiler()
    except ModelMissingError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    file_bytes = await image.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        profile = profiler.profile(file_bytes)
        features = profile["primary_face"]["normalized_measurements"]
        personality = infer_mbti(features)
        return {
            "profile": profile,
            "personality": personality,
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
