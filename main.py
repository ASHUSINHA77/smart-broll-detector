from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .detector import detect_broll_placements


class TranscriptSegment(BaseModel):
    id: str
    start: float
    end: float
    text: str


class Transcript(BaseModel):
    title: Optional[str] = None
    duration: float = Field(gt=0)
    segments: List[TranscriptSegment]


class Placement(BaseModel):
    segment_id: str
    start: float
    end: float
    reason: str
    score: Optional[int] = None


app = FastAPI(title="Smart B-roll Placement Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/detect", response_model=List[Placement])
def detect(transcript: Transcript) -> List[dict]:
    to_dict = getattr(transcript, "model_dump", transcript.dict)
    return detect_broll_placements(to_dict())
