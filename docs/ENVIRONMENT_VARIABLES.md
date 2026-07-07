# Environment Variables

## Backend (`backend/.env`, copy from `backend/.env.example`)

### LLM provider (choose ONE)

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | One of `openai`, `groq`, `openrouter`, `gemini`, `claude`. Controls which key/base-url/default-model is used. |
| `OPENAI_API_KEY` | Set only if `LLM_PROVIDER=openai`. |
| `GROQ_API_KEY` | Set only if `LLM_PROVIDER=groq`. Free tier available at console.groq.com — easiest way to try the AI chat. |
| `OPENROUTER_API_KEY` | Set only if `LLM_PROVIDER=openrouter`. |
| `GEMINI_API_KEY` | Set only if `LLM_PROVIDER=gemini`. Uses Gemini's OpenAI-compatible endpoint. |
| `CLAUDE_API_KEY` | Set only if `LLM_PROVIDER=claude`. Called via Anthropic's native Messages API. |
| `LLM_BASE_URL` | Optional override if you're using a custom/self-hosted OpenAI-compatible endpoint. |
| `LLM_MODEL_NAME` | Optional override of the default model for your chosen provider. |

**You do not need to set an API key to run the app.** Every AI Chat response still works without one — you just get the raw grounded fleet data instead of an LLM-phrased sentence, with a note explaining why (`API key not configured.`). Invalid keys and network failures are handled the same graceful way (`Invalid API key.` / connection error message) — nothing crashes.

### Auth

| Variable | Description |
|---|---|
| `JWT_SECRET` | Secret used to sign JWTs. **Change this to a long random value before any real deployment.** |
| `JWT_ALGORITHM` | Default `HS256`. No need to change. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes, default `60`. |

### Database

| Variable | Description |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string. Default `sqlite:///./fleet.db`. See `docs/DATABASE_SCHEMA.md` for switching to Postgres. |

### App

| Variable | Description |
|---|---|
| `ENVIRONMENT` | `development` or `production` — informational, shown on `/api/health`. |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins, e.g. `http://localhost:3000,https://yourapp.com`. |

## Frontend (`frontend/.env.local`, copy from `frontend/.env.local.example`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API, e.g. `http://localhost:8000` locally or `https://api.yourapp.com` in production. |

Next.js only exposes variables prefixed `NEXT_PUBLIC_` to the browser — don't put secrets here.
