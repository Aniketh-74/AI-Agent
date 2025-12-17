# AI Agent Project (React + FastAPI)

This project is a deployable interview/demo app showcasing a React + Vite frontend and a FastAPI backend that coordinates a small AI agent using GROQ as the LLM provider. It’s fully containerized, built with Cloud Build, and deployed to Google Cloud Run; sensitive keys are stored in Secret Manager and injected at runtime. Use it as a production-ready example of integrating custom LLM providers, CI/CD, and cloud-native secrets handling.

This repository contains a production-ready scaffold for an AI Agent application:

- Frontend: React (Vite)
- Backend: FastAPI calling OpenAI
# AI Agent — React + FastAPI + GROQ

A deployable interview/demo showcasing a small, opinionated AI agent built with modern tooling.

This repo is designed to be a launchpad for interviews and demos: it pairs a fast React + Vite frontend with a compact FastAPI backend that orchestrates calls to GROQ (the LLM provider). Everything is containerized and set up for CI/CD and Cloud Run deployment. Secrets are stored in Google Secret Manager and injected at runtime.

Live demo
-- Frontend (Cloud Run): https://test-frontend-329621052662.us-central1.run.app
-- Backend (Cloud Run):  https://test-backend-nb6x3zkdwq-uc.a.run.app

If you see errors or the service is down, check your Cloud Run console for the current URLs.

Highlights
- Small, focused codebase that demonstrates:
  - Integrating a custom LLM provider (GROQ) from FastAPI
  - Containerized frontend and backend (Docker multi-stage builds)
  - CI/CD-ready pipeline and Cloud Run deployment
  - Proper secret handling using Google Secret Manager

Quick local run (recommended for development)
1) Copy the example env and add secrets locally (DO NOT commit `.env`):

```powershell
copy .\.env.example .\.env
# edit .env and fill in GROQ_API_KEY locally
```

2) Start services with Docker Compose:

```powershell
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000

Run backend tests

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Environment variables
- The backend reads these env vars:
  - `GROQ_API_KEY` (required in production — use Secret Manager)
  - `GROQ_API_URL` (optional)
  - `GROQ_MODEL` (optional)

Secrets & deployment (short guide)
1) Store sensitive keys in Google Secret Manager (example name: `GROQ_API_KEY`).
2) Grant the Cloud Run runtime service account the role `roles/secretmanager.secretAccessor`.
3) Attach the secret to Cloud Run with `gcloud run services update <SERVICE> --update-secrets=GROQ_API_KEY=projects/<PROJECT_NUM>/secrets/GROQ_API_KEY:latest`.

This repository includes a `cloudbuild.deploy.yaml` example that demonstrates building images and deploying to Cloud Run while wiring secrets from Secret Manager.

Architecture at a glance
- Frontend: React + Vite (static build served by nginx in Docker)
- Backend: FastAPI (uvicorn) — small router with `/api/health` and `/api/ai` endpoints
- LLM: GROQ — called by the backend; responses are parsed with flexible fallbacks
- CI/CD: Cloud Build / GitHub Actions examples included

Usage notes and tips
- Never commit real API keys. Use `.env.example` with placeholders.
- Rotate keys immediately if a secret is leaked. Use Secret Manager versions to roll keys safely.
- When testing locally, set `VITE_API_URL` to point at your local backend (for dev server).

Demo checklist (what reviewers will look for)
- Clean separation between frontend and backend
- Secrets are injected at runtime from Secret Manager
- Docker images build reproducibly and deploy to Cloud Run
- Unit tests for backend logic (pytest)

Contributing
- Open an issue or a pull request. Keep changes small and add tests for new behavior.

License
- MIT

Contact
- Questions or help? Open an issue or reach out to the repo owner.

Enjoy — build something awesome!
