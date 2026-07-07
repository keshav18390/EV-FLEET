# EV Fleet Intelligence Multi-Agent System

An AI-powered fleet intelligence platform for EV logistics operations (think Zypp Electric-style scooter fleets) — vehicle tracking, battery analytics, predictive maintenance, delivery optimization, rider performance, and a 10-agent LangGraph AI assistant, backed by a FastAPI + SQLite backend and a Next.js 15 dashboard.

## What's actually in this project (read this first)

This was built and tested end-to-end in a sandboxed environment: the backend has a real automated test suite that passes (24 tests), the seed script and ML training scripts were actually run, and `next build` / `next lint` were actually run against the frontend with zero errors. A few things to be upfront about instead of overclaiming:

- **Scale**: seeded with 50 vehicles, 50 riders, 500 deliveries, 110+ maintenance records — a realistic, fast-to-generate dataset rather than 500 vehicles/5000 deliveries. You can bump the numbers in `backend/app/seed.py` (`seed_vehicles(db, 50)` etc.) and re-run if you want a bigger dataset.
- **Multi-agent framework**: LangGraph only (10 named agents in one graph). CrewAI was intentionally left out to avoid dependency conflicts, per a scoping conversation before this was built.
- **UI stack**: Tailwind + Recharts + lucide-react icons, no ShadCN/Framer Motion — a leaner stack that's less likely to break on a fresh install.
- **Docker**: `Dockerfile`s and `docker-compose.yml` are written to standard, correct conventions but could not be executed in the build environment (no Docker daemon available there). Test with `docker compose up --build` on your machine before relying on it.
- **ML models**: trained on the seeded (synthetic/random) data, so accuracy numbers are modest — they demonstrate a real, working training → save → load → predict pipeline, not tuned production models.

## Tech stack

**Backend**: FastAPI, Python 3.12, SQLAlchemy 2.0, SQLite, JWT auth (python-jose + passlib/bcrypt), LangGraph multi-agent orchestration, scikit-learn, pandas, reportlab (PDF), Faker (seed data), pytest.

**Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Recharts, TanStack React Query, Axios, lucide-react.

## Project structure

```
ev-fleet/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, routers, lifespan
│   │   ├── core/               # config, security, LLM client, auth deps
│   │   ├── db/                 # SQLAlchemy engine/session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── api/routes/         # auth, vehicles, riders, deliveries,
│   │   │                        maintenance, alerts, dashboard, chat,
│   │   │                        reports, admin, ml
│   │   ├── agents/              # LangGraph multi-agent system
│   │   ├── ml/                  # train.py, predict.py, saved models
│   │   └── seed.py              # demo data generator
│   ├── tests/                   # pytest suite (24 tests)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── login/, register/
│   │   └── (protected)/         # dashboard, vehicles, battery,
│   │                              maintenance, deliveries, riders,
│   │                              chat, alerts, reports, admin
│   ├── components/               # Sidebar, Topbar, MobileNav, ui.tsx
│   ├── lib/                      # api client, auth context, theme, types
│   ├── .env.local.example
│   └── Dockerfile
├── docs/                          # this documentation set
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Quick start (local, no Docker)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Open .env and set LLM_PROVIDER + the matching API key (see docs/ENVIRONMENT_VARIABLES.md).
# The app runs fine with NO key -- AI Chat just falls back to raw data instead of LLM-phrased answers.

python -m app.seed              # creates fleet.db and seeds demo data
python -m app.ml.train          # trains and saves the 4 ML models (optional but recommended)

uvicorn app.main:app --reload --port 8000
```

Backend is now live at http://localhost:8000. Interactive API docs: http://localhost:8000/docs

Demo logins (created by the seed script):
| Email | Password | Role |
|---|---|---|
| admin@evfleet.com | Admin@123 | admin |
| fleetmanager@evfleet.com | Fleet@123 | fleet_manager |
| opsmanager@evfleet.com | Ops@123 | operations_manager |

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:3000 and log in with one of the demo accounts above.

### 3. Run the backend tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

See `docs/INSTALLATION.md` for a more detailed walkthrough and `docs/TROUBLESHOOTING.md` if anything doesn't come up cleanly.

## Documentation index

- [`docs/INSTALLATION.md`](docs/INSTALLATION.md) — detailed setup steps
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, multi-agent flow diagram
- [`docs/API.md`](docs/API.md) — full endpoint reference
- [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) — tables and relationships
- [`docs/ENVIRONMENT_VARIABLES.md`](docs/ENVIRONMENT_VARIABLES.md) — every env var explained
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — Docker, Render, Railway, Vercel notes
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) — common issues and fixes

## AI Chat — how it actually works

The `/api/chat` endpoint runs a LangGraph graph with 10 named agents: a router, `fleet_monitoring`, `battery_health`, `maintenance_prediction`, `delivery_optimization`, `rider_performance`, `alert`, `report_generator`, `executive_dashboard`, `operations`, and a final `manager` agent that synthesizes the reply. The router uses deterministic keyword matching (reliable, no LLM cost) to pick a specialist, the specialist pulls **real numbers from your database** (never invented), and the manager agent phrases a natural-language answer using your configured LLM. If no API key is set, or the key is invalid, or the provider is unreachable, you still get a correct answer — just the raw grounded data with a note that AI phrasing wasn't available. Nothing crashes.

## License

Provided as-is for portfolio / educational use.
