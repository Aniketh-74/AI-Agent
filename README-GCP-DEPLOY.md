# Deploying this project to Google Cloud Run (quick guide)

This repository contains a FastAPI backend (`/backend`) and a static frontend built into an nginx image (`/frontend`). The project is Docker-ready and includes two Dockerfiles and a `docker-compose.yml` for local development.

This guide shows how to build and deploy both services to Google Cloud (Cloud Run) using Cloud Build.

Prerequisites

- Install and initialize the Google Cloud SDK (gcloud) and authenticate: `gcloud auth login`.
- Set your project and enable required APIs:

```powershell
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
```

- Ensure billing is enabled for the project.

Quick deploy using Cloud Build

1. Replace `YOUR_PROJECT_ID` with your GCP project id in the following command or export it as an env var:

```powershell
$env:PROJECT_ID = 'YOUR_PROJECT_ID'
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1
```

What this does

- Cloud Build will build the backend and frontend images and push them to `gcr.io/$PROJECT_ID`.
- It will then deploy both images to Cloud Run as services named `test-backend` and `test-frontend`.

Post-deploy

- The `gcloud run deploy` step prints each service URL. You can open the frontend URL in your browser and it will be accessible from anywhere.

Notes and customization

- If you prefer Artifact Registry, change the image names and push targets accordingly.
- You can set up a Cloud Build trigger from your Git repo to automatically build & deploy on push to main/master.
- Protect your API keys: store `GROQ_API_KEY` in Secret Manager and inject into Cloud Run service environment variables instead of embedding in code.

Security

- By default the services are deployed with `--allow-unauthenticated`. To restrict access, remove that flag and configure authentication.
