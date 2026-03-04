# Math Content Scoring API

Small API + web app for scoring K–12 math content: **difficulty**, **quality**, and **answer**. Built to demonstrate API-first design with auth and a minimal DB—suitable for demos (e.g. YC startups like Darcel building AI chatbots for education in developing countries).

## Run in 2 minutes

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: set API_KEY
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** for the web UI.  
Open **http://127.0.0.1:8000/docs** for OpenAPI (Swagger).

Default API key for local dev: `dev-key-change-in-production` (set in `.env` as `API_KEY`).

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
