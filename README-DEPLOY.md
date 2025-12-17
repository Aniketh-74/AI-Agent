# Deployment options

This project can be hosted in multiple ways. I prepared two recommended options:

A) Google Cloud Run (full backend + frontend as managed services)
B) Cloudflare Worker (GROQ proxy) + Vercel/Netlify (frontend static hosting)

Below are step-by-step instructions and the minimum secrets/config you need.

---

## A) Google Cloud Run (recommended if you want a single cloud-managed flow)

What you'll need:
- A Google Cloud project with billing enabled
- gcloud CLI installed and authenticated locally OR a service account key for CI automation

Quick manual deploy (local):

1. Configure gcloud and enable APIs:

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
```

2. Submit the Cloud Build defined in `cloudbuild.yaml` (this builds & deploys both services):

```powershell
# from repo root
$env:PROJECT_ID = 'YOUR_PROJECT_ID'
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1
```

3. After the build, Cloud Build will print the Cloud Run URLs for `test-backend` and `test-frontend`.

CI automation (GitHub Actions):
- I added a GitHub Actions workflow at `.github/workflows/gcp-cloudbuild.yml` that runs on push to `main`.
- Create these repository secrets:
  - `GCP_SA_KEY` — JSON service account key (base64 or raw JSON content). The service account must have permissions: `roles/cloudbuild.builds.editor`, `roles/run.admin`, and `roles/storage.admin` (or use Owner for convenience in a demo project).
  - `GCP_PROJECT` — your GCP project id.
  - Optional: `GCP_REGION` — e.g. `us-central1`.

When those secrets are set, pushing to `main` triggers a build and Cloud Run deploy.

Security note and secret management (recommended)
- It is strongly recommended you store `GROQ_API_KEY` in Google Secret Manager and attach it to the Cloud Run service rather than embedding it in CI or container images.

Create and populate a secret in Secret Manager (one-time):

```powershell
# Create the secret (one-time)
gcloud secrets create GROQ_API_KEY --replication-policy="automatic"

# Add the secret value (paste your key or pipe from a file). Example: pipe from an env variable (PowerShell):
$env:GROQ_API_KEY = 'PASTE_YOUR_KEY_HERE'
[System.Console]::OpenStandardOutput() | ForEach-Object { $env:GROQ_API_KEY } | gcloud secrets versions add GROQ_API_KEY --data-file=-

# Or simply: echo "YOUR_GROQ_API_KEY" | gcloud secrets versions add GROQ_API_KEY --data-file=-
```

Attach the secret to your backend Cloud Run service so the runtime can access it as a secret environment variable (this example uses `test-backend` and `us-central1` — replace with your values):

```powershell
# Replace YOUR_PROJECT_ID and REGION if different
gcloud run services update test-backend \
  --region=us-central1 \
  --update-secrets=GROQ_API_KEY=projects/YOUR_PROJECT_ID/secrets/GROQ_API_KEY:latest
```

What this does:
- The service runtime is granted access to the secret and will expose the secret value to the container as an environment variable named `GROQ_API_KEY`.
- If you redeploy via Cloud Build, the secret binding is preserved.

Set the frontend's API URL (if you deployed the frontend to Cloud Run as `test-frontend`):

```powershell
# Replace BACKEND_URL with the Cloud Run URL printed by Cloud Build (or the service URL from the console)
gcloud run services update test-frontend --region=us-central1 --set-env-vars=VITE_API_URL="https://YOUR_BACKEND_URL"
```

If you host the frontend elsewhere (Vercel/Netlify), set the environment variable `VITE_API_URL` in that platform's project settings to the backend's Cloud Run URL.

---

## B) Cloudflare Worker (proxy) + Vercel/Netlify frontend (free/cheap)

Overview:
- The Worker holds your GROQ API key as a secret and proxies frontend requests to the GROQ API.
- The frontend is deployed as a static site on Vercel/Netlify/GitHub Pages and calls the Worker URL as `VITE_API_URL`.

Files prepared:
- `worker/index.js` — Worker proxy implementation.
- `worker/wrangler.toml` — initial Wrangler config.
- `worker/README.md` — instructions to publish.

Steps to publish the Worker (interactive):

```powershell
cd worker
# login with your Cloudflare account (interactive)
wrangler login
# set your GROQ key as a secret
wrangler secret put GROQ_API_KEY
# deploy
wrangler deploy
```

- Wrangler will prompt to register a `workers.dev` subdomain if you don't have one. Keep note of the resulting worker URL (e.g. `https://my-proxy.your-subdomain.workers.dev`).
- Set `VITE_API_URL` in your frontend hosting platform (Vercel/Netlify) to the Worker URL, then deploy the frontend.

Automatic frontend deploy to Vercel (CI)
--------------------------------------
I added a GitHub Actions workflow `.github/workflows/deploy-frontend-vercel.yml` that builds the `frontend` and deploys to Vercel on push to `main`.

To enable it, add these repository secrets in GitHub:
- `VERCEL_TOKEN` — a personal token from Vercel (https://vercel.com/account/tokens)
- `VERCEL_ORG_ID` — (from Vercel project settings)
- `VERCEL_PROJECT_ID` — (from Vercel project settings)

When those are set, pushing to `main` will build the frontend and call Vercel to publish the `frontend` as a production deployment.

Frontend deploy (Vercel example):
- Connect your GitHub repository to Vercel and set Environment Variable `VITE_API_URL` to the Worker URL.
- Deploy the `frontend` project (Vercel will run `npm run build` then publish static files).

---

## Quick validation after deployment
- Open the frontend URL. Submit a prompt or run a workflow.
- For Cloud Run: the frontend should call the backend directly.
- For Worker+Vercel: frontend calls the Worker, which proxies to GROQ (keep your GROQ_API_KEY secret in the Worker).

If you want, I can:
- Add a GitHub Actions workflow that deploys the static `frontend` to GitHub Pages or Netlify automatically (requires corresponding tokens).
- Add Cloud Build steps to inject `GROQ_API_KEY` from Secret Manager into Cloud Run service env vars (requires Secret Manager & IAM privileges).

Tell me which option you'd like to use (A or B) and whether you want me to add any extra automation (GitHub Actions to deploy frontend, Cloud Run env var injection steps, or a small script to produce the frontend build).