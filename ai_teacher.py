"""
AI teacher: one response with answer, difficulty, relevance to topic, explanation.
Uses OpenAI when OPENAI_API_KEY is set; otherwise fallback from scoring + SymPy.
"""

import json
from config import settings
from scoring import estimate_difficulty
from answer_engine import get_answer


SYSTEM_PROMPT = """You are a friendly math teacher for K-12 students. Given a math problem and an optional topic, respond with a JSON object only (no other text) with exactly these keys:
- "answer": the numerical or symbolic answer; include brief steps if helpful (string).
- "difficulty": one of "Easy", "Medium", "Hard" plus one short sentence why (string).
- "relevance_to_topic": if a topic was given, one sentence on how well the problem fits; else "No topic specified." (string).
- "explanation": a brief, kind step-by-step explanation for a student (string).

Keep each value concise. Use simple language."""


def _fallback_response(problem_text: str, topic: str | None) -> dict:
    """When no OpenAI key: use heuristics + SymPy for answer; placeholder explanation."""
    score_result = estimate_difficulty(problem_text, topic, None)
    answer_data = get_answer(problem_text)
    answer_text = answer_data.get("answer_text", "")
    relevance = f"This problem fits the topic '{topic}'." if topic else "No topic specified."
    explanation = (
        "Add your OpenAI API key in .env (OPENAI_API_KEY) to get an AI-generated "
        "step-by-step explanation and a more accurate difficulty and relevance."
    )
    return {
        "answer": answer_text,
        "difficulty": score_result.difficulty.capitalize(),
        "relevance_to_topic": relevance,
        "explanation": explanation,
    }


def get_ai_teacher_response(problem_text: str, topic: str | None = None) -> dict:
    """
    Returns dict: answer, difficulty, relevance_to_topic, explanation.
    Uses OpenAI if OPENAI_API_KEY is set; else fallback.
    """
    if not settings.openai_api_key:
        return _fallback_response(problem_text, topic)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        user_content = f"Math problem: {problem_text}"
        if topic:
            user_content += f"\nTopic to check relevance: {topic}"

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=500,
        )
        text = (resp.choices[0].message.content or "").strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {
                "answer": text[:200],
                "difficulty": "Medium",
                "relevance_to_topic": "No topic specified." if not topic else f"Relevance to '{topic}'.",
                "explanation": text,
            }
        return {
            "answer": data.get("answer", ""),
            "difficulty": data.get("difficulty", "Medium"),
            "relevance_to_topic": data.get("relevance_to_topic", "No topic specified."),
            "explanation": data.get("explanation", ""),
        }
    except Exception as e:
        return {
            "answer": "Sorry, the AI teacher couldn't respond.",
            "difficulty": "—",
            "relevance_to_topic": "—",
            "explanation": f"Error: {str(e)}. Check your OPENAI_API_KEY in .env.",
        }
