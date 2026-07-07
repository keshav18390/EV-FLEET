# Deployment Guide

## Option A: Docker Compose (recommended for a single VM)

```bash
cp backend/.env.example backend/.env    # fill in your values
docker compose up --build -d
```

This builds and runs both services:
- Backend on port 8000 (seeds the DB automatically on first boot)
- Frontend on port 3000

> **Note**: the `Dockerfile`s and `docker-compose.yml` in this project follow standard, well-tested conventions but could not be executed inside the sandboxed build environment (no Docker daemon available there). Run `docker compose up --build` yourself and check `docker compose logs` before trusting it in production — if anything's off, the backend Dockerfile and compose file are simple enough to hand-fix.

## Option B: Render

1. Push this repo to GitHub.
2. Create a **Web Service** for the backend: root directory `backend`, build command `pip install -r requirements.txt`, start command `python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Add your env vars from `backend/.env.example` in Render's dashboard.
3. Create a **Static Site** or second **Web Service** for the frontend: root directory `frontend`, build command `npm install && npm run build`, start command `npm run start`. Set `NEXT_PUBLIC_API_URL` to your backend's Render URL.
4. Update `CORS_ORIGINS` on the backend to include your frontend's Render URL.

## Option C: Railway

1. `railway init` inside the repo, or connect the GitHub repo in the Railway dashboard.
2. Add two services pointing at `backend/` and `frontend/` respectively (Railway auto-detects Dockerfiles if present — it will use the ones in this repo).
3. Set the same environment variables as above per-service.
4. Railway assigns each service a public URL — use the backend's URL for the frontend's `NEXT_PUBLIC_API_URL`.

## Option D: Vercel (frontend only) + any host for backend

Vercel is a great fit for the Next.js frontend specifically:

1. Import the repo in Vercel, set the root directory to `frontend`.
2. Set `NEXT_PUBLIC_API_URL` to wherever your backend is hosted (Render/Railway/EC2/etc — Vercel doesn't run the Python backend).
3. Deploy.

## Option E: A plain VM (EC2, DigitalOcean, etc.)

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit values
python -m app.seed
python -m app.ml.train
# Run behind a process manager, e.g.:
pip install gunicorn
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000

# Put Nginx in front for TLS + reverse proxy to :8000 and :3000
```

For the frontend on the same VM: `npm install && npm run build && npm run start` (or use `pm2` to keep it alive), and reverse-proxy port 3000 through Nginx too.

## Production checklist

- [ ] Set a long random `JWT_SECRET` (never use the default).
- [ ] Set `ENVIRONMENT=production`.
- [ ] Restrict `CORS_ORIGINS` to your real frontend domain(s) only.
- [ ] Put a real LLM API key in place if you want AI-phrased chat replies.
- [ ] Consider moving from SQLite to Postgres for concurrent-write safety at scale (see `docs/DATABASE_SCHEMA.md`).
- [ ] Put HTTPS in front of both services (Nginx/Caddy/hosting provider's TLS).
- [ ] Re-run `python -m app.ml.train` periodically as more real data accumulates.
