# Troubleshooting Guide

## Backend won't start / `ModuleNotFoundError`
Make sure the virtual environment is activated (`source venv/bin/activate`) and dependencies are installed (`pip install -r requirements.txt`). Re-run from inside the `backend/` directory since imports are relative to `app.*`.

## `sqlalchemy.exc.OperationalError: no such table`
Run `python -m app.seed` at least once — it creates all tables and the demo data. If you deleted `fleet.db` manually, just re-run the seed script.

## Login fails with "Invalid email or password" even with the demo credentials
Confirm you actually ran `python -m app.seed` (it prints the demo logins on success) and that you copied `.env.example` to `.env` before starting the server — without `.env`, some default settings are still fine, but double-check `DATABASE_URL` didn't change and point somewhere new/empty.

## Frontend shows "Could not reach the server. Is the backend running?"
1. Confirm the backend is running: `curl http://localhost:8000/api/health`.
2. Confirm `frontend/.env.local` has `NEXT_PUBLIC_API_URL` pointing at the right host/port.
3. Restart `npm run dev` after changing `.env.local` — Next.js only reads env files at startup.

## CORS errors in the browser console
Add your frontend's exact origin (protocol + host + port) to `CORS_ORIGINS` in `backend/.env`, comma-separated if you have more than one, then restart the backend.

## AI Chat replies say "API key not configured."
This is expected and not a bug — it means `LLM_PROVIDER` is set but the matching API key env var is empty. The reply still contains real fleet data; it's just not LLM-phrased. Add a key (see `docs/ENVIRONMENT_VARIABLES.md`) and restart the backend to enable phrased replies.

## AI Chat replies say "Invalid API key."
The key for your chosen `LLM_PROVIDER` is set but rejected by the provider. Double check you copied the whole key with no extra whitespace, and that it matches the provider you set in `LLM_PROVIDER` (e.g. don't put an OpenAI key while `LLM_PROVIDER=groq`).

## `bcrypt` warning about `__about__` attribute
This is a known cosmetic incompatibility between certain `passlib` and `bcrypt` versions. This project pins `bcrypt==4.0.1` in `requirements.txt` specifically to avoid it — if you see the warning, check you installed from the pinned `requirements.txt` rather than a cached/different environment.

## ML prediction endpoints return heuristic-looking numbers
If `python -m app.ml.train` hasn't been run yet, `app/ml/predict.py` automatically falls back to simple heuristics so the API never errors. Run the training script to get real model-based predictions.

## `next build` fails trying to fetch Google Fonts
This project intentionally uses system fonts (no `next/font/google`) specifically so builds don't depend on network access to Google's font CDN. If you've since added a Google Font import yourself and hit this in a network-restricted environment, either restore network access during build or switch back to a system font stack in `app/layout.tsx` / `app/globals.css`.

## Port already in use (`8000` or `3000`)
Backend: `uvicorn app.main:app --reload --port 8001` (and update `NEXT_PUBLIC_API_URL` accordingly).
Frontend: `npm run dev -- -p 3001`.

## Tests fail with a leftover `test_fleet.db`
Delete it and re-run: `rm -f backend/test_fleet.db && pytest backend/tests -v`. The test suite is also designed to drop/recreate tables at session start, so this should be rare.

## Still stuck?
Check the interactive API docs at `http://localhost:8000/docs` to confirm the backend's actual current behavior for any endpoint — it's generated live from the real code, not from this document.
