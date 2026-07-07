# Architecture

## High-level overview

```
┌──────────────────────┐        HTTPS/JSON         ┌───────────────────────────┐
│   Next.js Frontend    │ ◄────────────────────────► │      FastAPI Backend      │
│  (React 19, Tailwind, │        JWT Bearer auth      │  (Python 3.12, SQLAlchemy)│
│  Recharts, TanStack   │                             │                           │
│  React Query)         │                             │  ┌─────────────────────┐  │
└──────────────────────┘                             │  │  LangGraph Agents    │  │
                                                       │  │  (10-agent system)   │  │
                                                       │  └──────────┬──────────┘  │
                                                       │             │             │
                                                       │  ┌──────────▼──────────┐  │
                                                       │  │   ML Models (sklearn) │ │
                                                       │  │  battery/maintenance/ │ │
                                                       │  │  delay/rider models   │ │
                                                       │  └──────────────────────┘  │
                                                       │             │             │
                                                       │  ┌──────────▼──────────┐  │
                                                       │  │   SQLite Database    │  │
                                                       │  │  (SQLAlchemy ORM)    │  │
                                                       │  └──────────────────────┘  │
                                                       └───────────────────────────┘
                                                                     │
                                                        Configurable LLM Provider
                                                     (OpenAI / Groq / OpenRouter /
                                                      Gemini / Claude via one env var)
```

## Multi-agent chat flow (LangGraph)

```
                              ┌────────────┐
                 user query → │   router   │  (keyword classification, no LLM needed)
                              └─────┬──────┘
                                    │
        ┌────────────┬─────────────┼─────────────┬─────────────┬───────────────┐
        ▼            ▼             ▼             ▼             ▼               ▼
 fleet_monitoring battery_health maintenance_ delivery_    rider_performance   alert
                                  prediction   optimization
        │            │             │             │             │               │
        └────────────┴─────────────┴──────┬──────┴─────────────┴───────────────┘
                                            │  (plus report_generator,
                                            │   executive_dashboard, operations)
                                            ▼
                                    ┌──────────────┐
                                    │ manager agent │  synthesizes final reply using
                                    │  (10th agent) │  the configured LLM, grounded
                                    └──────┬───────┘  strictly in DB facts gathered above
                                            ▼
                                          END → JSON { reply, agent }
```

Each specialist node queries the database directly (via `app/agents/tools.py`) and writes a `db_context` string of **real facts** into the LangGraph state. The `manager` node is the only one that calls the LLM, and it's instructed to use only the provided facts — this keeps hallucination risk low. If the LLM call fails for any reason (no key, invalid key, network issue), `manager` falls back to returning the raw grounded facts directly, so the chat feature never actually breaks.

## Request lifecycle example: "Which scooters need servicing?"

1. Frontend `ChatPage` POSTs `{ message: "Which scooters need servicing?" }` to `/api/chat` with the JWT in the `Authorization` header.
2. FastAPI's `get_current_user` dependency validates the token.
3. `run_chat_agent` builds and invokes the LangGraph graph.
4. `router` matches "servic" → routes to `maintenance_prediction`.
5. `maintenance_prediction` queries `Vehicle` rows where `odometer_km >= next_service_due_km`, plus total maintenance spend.
6. `manager` calls the configured LLM with that grounded context and a system prompt restricting it to the provided facts (or falls back gracefully).
7. Response `{ reply, agent: "Maintenance Prediction Agent" }` is returned and rendered in the chat UI with the agent name shown above the bubble.

## Backend layering

- **`api/routes/`** — thin HTTP layer: request validation (Pydantic), calls into models/agents, returns typed responses.
- **`models/`** — SQLAlchemy ORM definitions, one file per entity.
- **`schemas/`** — Pydantic schemas for request/response validation, decoupled from ORM models.
- **`core/`** — cross-cutting concerns: settings (env loading), JWT + password hashing, the unified LLM client, auth dependencies.
- **`agents/`** — the LangGraph multi-agent system and its DB-query tools.
- **`ml/`** — training script (`train.py`), inference module (`predict.py`) with graceful fallback if models aren't trained yet.

## Frontend layering

- **`app/(protected)/`** — a Next.js route group; its `layout.tsx` enforces auth (redirects to `/login` if not signed in) and renders the shared `Sidebar` + page content.
- **`app/login`, `app/register`** — public auth pages, outside the protected group.
- **`lib/auth-context.tsx`** — React context wrapping login/register/logout, backed by `localStorage` for the JWT.
- **`lib/api.ts`** — a single Axios instance with a request interceptor that attaches the JWT, and a response interceptor that redirects to `/login` on 401.
- **`components/ui.tsx`** — shared primitives (`Card`, `StatCard`, `Badge`, pagination, loading/empty/error states) used across every page for visual consistency.

## Why LangGraph only (not LangGraph + CrewAI)

The two frameworks have overlapping dependency trees (different pinned versions of `pydantic`, `langchain-core`, etc.) that commonly conflict when installed together. Rather than risk a broken `pip install` on your machine, this build uses LangGraph alone, structured so all 10 required agents are still present and communicating through the graph — CrewAI's main value-add (role-based crews with a task manager) is effectively replicated here by the router + manager pattern.

## Why the LLM call only happens once per chat turn

Every specialist agent does deterministic, grounded data-gathering (fast, free, no hallucination risk). Only the final `manager` node calls the LLM, and only to turn already-correct facts into readable prose. This means: (a) you get exactly one LLM call per user message, keeping costs predictable, and (b) even a wrong-shaped LLM response can't corrupt the underlying facts shown to the user.
