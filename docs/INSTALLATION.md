# Installation Guide

## Prerequisites

- Python 3.11 or 3.12
- Node.js 20+ (tested with Node 22)
- npm 10+
- (Optional) Docker + Docker Compose, if you want containers instead of running locally

## 1. Unzip the project

```bash
unzip ev-fleet-intelligence.zip
cd ev-fleet
```

## 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate            # Windows PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and configure your LLM provider (see `docs/ENVIRONMENT_VARIABLES.md`). You can leave the API key blank — the app works without one, just without AI-phrased chat replies.

Generate the database and demo data:

```bash
python -m app.seed
```

You should see output like:

```
Seeded demo users (admin@evfleet.com / Admin@123, etc.)
Seeded 50 vehicles
Seeded 50 riders
Seeded 500 deliveries
Seeded 110 maintenance records
Seeded 37 alerts
```

(Re-running `python -m app.seed` after data already exists is a safe no-op. Delete `fleet.db` if you want to reseed from scratch.)

Train the ML models (optional — the API falls back to heuristics if you skip this):

```bash
python -m app.ml.train
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it's up: open http://localhost:8000/api/health — you should see `{"status":"ok", ...}`. Interactive Swagger docs are at http://localhost:8000/docs.

## 3. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000. You'll be redirected to `/login`. Use one of the demo accounts:

- admin@evfleet.com / Admin@123
- fleetmanager@evfleet.com / Fleet@123
- opsmanager@evfleet.com / Ops@123

## 4. Run backend tests (optional but recommended)

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

All 24 tests should pass.

## 5. Production build check (optional)

```bash
cd frontend
npm run build     # verifies zero TypeScript/lint/build errors
npm run start     # serves the production build on port 3000
```

## Next steps

- Add a real LLM key (Groq's free tier is the easiest to get started with) to unlock AI-phrased chat replies — see `docs/ENVIRONMENT_VARIABLES.md`.
- Read `docs/ARCHITECTURE.md` to understand how the multi-agent system and frontend fit together.
- See `docs/DEPLOYMENT.md` when you're ready to put this on a server.
