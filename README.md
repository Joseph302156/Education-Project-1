# Math AI Teacher

Web app for students and teachers: enter a math problem (numbers or natural language), optionally a topic, and get **answer**, **difficulty**, **relevance to topic**, and **explanation** from an AI teacher chatbox.

## Run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: add OPENAI_API_KEY for real AI responses
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** — that’s the main site (chatbox). No login or API key needed for students/teachers.

**AI responses:** Set `OPENAI_API_KEY` in `.env` to use OpenAI for answer, difficulty, relevance, and explanation. Without it, the app still works using built-in scoring and SymPy for equations, with a short message suggesting you add the key.

---

## API

- **POST /v1/score** — Score a math problem (auth required).
- **GET /health** — Health check (no auth).

### Auth

- **Header:** `X-API-Key: <key>` or `Authorization: Bearer <key>`

### Request body (JSON)

| Field          | Type   | Required | Description                          |
|----------------|--------|----------|--------------------------------------|
| `problem_text` | string | yes      | Math problem as text or equation    |
| `topic`        | string | no       | Topic to link to (e.g. algebra)     |
| `grade_level`  | int    | no       | Target grade 1–12                   |

### Response

- `difficulty` — `"easy"` \| `"medium"` \| `"hard"`
- `difficulty_score` — 0–1
- `quality_score` — 0–1
- `quality_factors` — e.g. `length_ok`, `has_question_mark`
- `readability_notes` — short note
- `answer` — `{ "answer_text", "steps", "solved" }` (SymPy for equations; word problems get a placeholder; production would use an LLM)

---

## cURL examples

```bash
# Score a problem (default key)
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{"problem_text": "Solve for x: 2*x + 3 = 11", "topic": "algebra", "grade_level": 6}'

# With Bearer token
curl -X POST http://127.0.0.1:8000/v1/score \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-key-change-in-production" \
  -d '{"problem_text": "What is 15% of 80?"}'
```

---

## Stack

- **Backend:** FastAPI, OpenAPI at `/docs`, API key or Bearer auth
- **Scoring:** Heuristics (word count, numbers, grade-level keywords)
- **Answer:** SymPy for equations/expressions; word problems note “plug in LLM here”
- **DB:** SQLite (`content` + `scores` tables), created on startup
- **Frontend:** Single-page form at `/` calling the API

This is the kind of API you’d design for a backend that serves content scoring and answers to an education product.
