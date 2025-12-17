# AI Agent Project (React + FastAPI)

This project is a deployable interview/demo app showcasing a React + Vite frontend and a FastAPI backend that coordinates a small AI agent using GROQ as the LLM provider. It’s fully containerized, built with Cloud Build, and deployed to Google Cloud Run; sensitive keys are stored in Secret Manager and injected at runtime. Use it as a production-ready example of integrating custom LLM providers, CI/CD, and cloud-native secrets handling.

This repository contains a production-ready scaffold for an AI Agent application:

- Frontend: React (Vite)
- Backend: FastAPI calling OpenAI
- Containerized with Docker and docker-compose
- CI/CD template with GitHub Actions to build & push Docker images (placeholders for secrets)

Quickstart (local, using Docker)

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
2. Run:

```powershell
# from repository root
docker-compose up --build
```

- Frontend will be exposed on http://localhost:3000
- Backend API on http://localhost:8000 (used by frontend)

## Deployment — Live (Cloud Run)

This project is deployed to Google Cloud Run (no custom domain required). Use the URLs below to access the running demo:

- Frontend: https://test-frontend-329621052662.us-central1.run.app
- Backend:  https://test-backend-329621052662.us-central1.run.app

Quick demo steps:

1. Open the frontend URL in a browser to load the app.
2. The frontend communicates with the backend at the backend URL. If you inspect network calls (DevTools) you should see requests to `/api/` endpoints.
3. Health check:

```powershell
curl -s https://test-backend-329621052662.us-central1.run.app/api/health
# expected output: {"status":"ok"}
```

Notes:
- The backend has CORS configured to accept requests from the deployed frontend URL.
- Secrets (GROQ_API_KEY) are stored in Secret Manager and attached to the backend service.

Local dev (frontend)

```powershell
cd frontend
npm install
# set VITE_API_URL during dev if backend URL differs
npm run dev
```

- Replace the OpenAI usage with the Chat API if you prefer a chat-style agent.

# AI Agent (React frontend + FastAPI backend using GROQ)

This project is a minimal deployment-ready template combining a React (Vite) frontend and a FastAPI backend which calls GROQ AI.

Features

- React + Vite frontend (Docker multi-stage build with nginx)
- FastAPI backend with an `/api/ai` endpoint that calls GROQ AI and `/api/health` healthcheck
- docker-compose for local development
- GitHub Actions workflow to build & push Docker images

Environment

- Create a `.env` file at the repository root (copy `.env.example`) and set:
  - `GROQ_API_KEY` — your GROQ API key
  - Optional: `GROQ_API_URL` if you have a custom endpoint
  - Optional: `GROQ_MODEL` to select a model

Local development with Docker Compose

1. Copy `.env.example` -> `.env` and fill in `GROQ_API_KEY`.
2. From the project root (where `docker-compose.yml` lives):

```powershell
docker-compose up --build
```

- Backend will be available at http://localhost:8000
- Frontend will be available at http://localhost:3000 (served from nginx)

Run backend tests locally (without Docker)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Notes on GROQ integration

- The backend reads `GROQ_API_KEY`, `GROQ_API_URL`, and `GROQ_MODEL` from environment variables.
- The code uses a plain HTTP POST to the GROQ endpoint; payload and response parsing include flexible fallbacks since providers differ in their JSON shapes.

CI / CD

- The workflow in `.github/workflows/ci-cd.yml` builds and pushes Docker images to Docker Hub using secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
- Add additional deployment steps for your target cloud (Cloud Run, Render, Azure App Service, etc.).

Security

- Do NOT commit your `.env` or any secret keys into git. Use repository secrets for CI and cloud credentials.

Next steps I can do for you

- Wire automatic deploy to a cloud provider (pick Cloud Run, Render, Azure, or AWS ECS)
- Switch the backend to a streaming Chat-like interface if GROQ supports one
- Add authentication, rate-limiting, or prototype a usage dashboard

If you'd like me to add a cloud deploy step now, tell me which provider to target and I will add it to the workflow and provide required secrets/instructions.
