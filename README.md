# Job Match API

A small FastAPI service for managing candidate profiles and job postings. It is
structured for a transparent, rule-based recommendation engine.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Create the PostgreSQL database configured by `DATABASE_URL`, then apply schema
migrations:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Tests

```bash
pytest
```

Tests use an isolated SQLite database. Production configuration continues to
target PostgreSQL.

## Endpoints

- `POST /candidates`
- `GET /candidates/{candidate_id}`
- `POST /jobs`
- `GET /jobs/{job_id}`
- `GET /candidates/{candidate_id}/recommendations?limit=10`
- `GET /jobs/{job_id}/recommendations?limit=10`

## Docker workflow

```bash
cp .env.example .env
# Edit POSTGRES_PASSWORD (and optionally the score weights) in .env.
docker compose up --build
```

The API runs at `http://localhost:8000`; Swagger is at
`http://localhost:8000/docs`. Compose waits for PostgreSQL's health check, then
applies Alembic migrations before starting the API.

To load the deterministic demonstration dataset after the stack is running:

```bash
docker compose exec api python seed.py
```

`seed.py` deliberately replaces all candidate and job records before loading 8
candidates and 25 jobs. This makes demo data reproducible, so only use it on a
development database. For local non-Docker use, configure `DATABASE_URL`, run
`alembic upgrade head`, then run `python seed.py`.

## Recommendation scoring

Recommendations are deterministic, transparent, and ranked before the requested
limit is applied. A missing must-have skill excludes a job entirely. Eligible
jobs receive a score out of 100:

- Skills: 50 points — 40 for all must-haves (already satisfied), plus up to 10
  proportionally for nice-to-have matches. Jobs with no nice-to-haves receive
  the full 10 points.
- Experience: 20 points — full credit at or above the requirement; otherwise
  `20 * candidateYears / requiredYears`, clamped to the range. Experience is a
  soft criterion: candidates below the requirement remain eligible so strong
  candidates are not discarded, while the shortfall remains visible.
- Location: 15 points for an exact normalized match, 10 for a remote role with
  a location mismatch, otherwise 0.
- Salary: 15 points if the full salary range meets expectation, 0 if its maximum
  is below expectation, otherwise `15 * (max - expected) / (max - min)`.
  Equal salary endpoints safely yield 15 or 0.

All comparisons normalize case and whitespace where relevant. Component and
overall scores are clamped and rounded to two decimal places. The endpoint
returns `candidateId`, ranked `results`, and each result's complete breakdown.

Reverse recommendations (`GET /jobs/{job_id}/recommendations`) reuse the exact
same scorer, with a fixed job and candidates ranked by their matching score.

## Configurable weights

The scorer accepts a validated `ScoringWeights` object. Defaults are 50 skills,
20 experience, 15 location, and 15 salary. Environment overrides are available
through the `SCORING_*_WEIGHT` values in `.env`; all values must be non-negative
and total 100.
