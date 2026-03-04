import re
from dataclasses import dataclass

# Grade-level keyword tiers (simplified): lower = easier
GRADE_KEYWORDS = {
    "elementary": ("add", "subtract", "count", "sum", "total", "half", "double", "digit"),
    "middle": ("equation", "variable", "solve", "fraction", "percent", "ratio", "algebra"),
    "high": ("derivative", "integral", "quadratic", "polynomial", "logarithm", "trigonometry"),
}


@dataclass
class ScoreResult:
    difficulty: str  # "easy" | "medium" | "hard"
    difficulty_score: float  # 0-1
    quality_score: float  # 0-1
    quality_factors: dict
    topic_match: str | None  # suggested topic or None
    readability_notes: str


def _count_numbers(text: str) -> int:
    return len(re.findall(r"\d+\.?\d*", text))


def _word_count(text: str) -> int:
    return len(text.split())


def _grade_keyword_tier(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in GRADE_KEYWORDS["high"]):
        return "high"
    if any(k in lower for k in GRADE_KEYWORDS["middle"]):
        return "middle"
    if any(k in lower for k in GRADE_KEYWORDS["elementary"]):
        return "elementary"
    return "elementary"


def estimate_difficulty(problem_text: str, topic: str | None, grade_level: int | None) -> ScoreResult:
    words = _word_count(problem_text)
    numbers = _count_numbers(problem_text)
    tier = _grade_keyword_tier(problem_text)

    # Heuristic: more words + numbers + higher tier => harder
    raw = 0.0
    raw += min(words / 50, 1.0) * 0.3
    raw += min(numbers / 8, 1.0) * 0.2
    if tier == "high":
        raw += 0.4
    elif tier == "middle":
        raw += 0.2

    if grade_level is not None:
        # Adjust by requested grade: if problem looks harder than grade, bump score
        grade_norm = max(1, min(12, grade_level)) / 12
        if raw > grade_norm + 0.2:
            raw = min(1.0, raw + 0.1)

    if raw < 0.35:
        difficulty = "easy"
    elif raw < 0.65:
        difficulty = "medium"
    else:
        difficulty = "hard"

    # Quality: length, clarity (has question mark or "find/solve"), no obvious garbage
    quality = 0.5
    quality_factors = {"length_ok": words >= 5, "has_question_mark": "?" in problem_text}
    if words >= 5:
        quality += 0.15
    if "?" in problem_text or "find" in problem_text.lower() or "solve" in problem_text.lower():
        quality += 0.2
    if 10 <= words <= 150:
        quality += 0.15
    quality = min(1.0, quality)

    readability = "Short problem." if words < 10 else "Reasonable length."
    if numbers > 5:
        readability += " Number-heavy; may need calculator."

    return ScoreResult(
        difficulty=difficulty,
        difficulty_score=round(raw, 2),
        quality_score=round(quality, 2),
        quality_factors=quality_factors,
        topic_match=topic if topic else None,
        readability_notes=readability,
    )
