from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from auth import verify_api_key
from database import init_db, store_content_and_scores
from scoring import estimate_difficulty, ScoreResult
from answer_engine import get_answer
from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    problem_text: str = Field(..., min_length=1, description="Math problem as text or equation")
    topic: str | None = Field(None, description="Topic to check fit for (e.g. algebra, fractions)")
    grade_level: int | None = Field(None, ge=1, le=12, description="Target grade level 1-12")


class ScoreResponse(BaseModel):
    difficulty: str
    difficulty_score: float
    quality_score: float
    quality_factors: dict
    topic_match: str | None
    readability_notes: str
    answer: dict
    content_id: int | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Math Content Scoring API",
    description="Score math problems: difficulty, quality, and get an answer. API-first, with auth.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    index = static_dir / "index.html"
    if index.exists():
        return index.read_text(encoding="utf-8")
    return "<p>Math Content Scoring API. See <a href='/docs'>/docs</a>.</p>"


@app.post("/v1/score", response_model=ScoreResponse)
async def score(
    body: ScoreRequest,
    _: str = Depends(verify_api_key),
):
    score_result: ScoreResult = estimate_difficulty(
        body.problem_text, body.topic, body.grade_level
    )
    answer = get_answer(body.problem_text)
    content_id = store_content_and_scores(
        body.problem_text,
        body.topic,
        body.grade_level,
        score_result.difficulty,
        score_result.difficulty_score,
        score_result.quality_score,
        answer.get("answer_text", ""),
    )
    return ScoreResponse(
        difficulty=score_result.difficulty,
        difficulty_score=score_result.difficulty_score,
        quality_score=score_result.quality_score,
        quality_factors=score_result.quality_factors,
        topic_match=score_result.topic_match,
        readability_notes=score_result.readability_notes,
        answer=answer,
        content_id=content_id,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
