# Cloudflare Worker proxy (groq-proxy)

This folder contains a minimal Cloudflare Worker that proxies /api/\* requests to the GROQ API. The Worker keeps your GROQ API key secret via Wrangler secrets.

Deploy steps (local)

1. Install Wrangler (Cloudflare CLI):

```powershell
npm install -g wrangler
wrangler login
```

2. Set your account id (optional) or let Wrangler detect it. In `wrangler.toml` you can set `account_id`.

3. Add secrets (secure):

```powershell
wrangler secret put GROQ_API_KEY
# optionally
wrangler secret put GROQ_API_URL
wrangler secret put GROQ_MODEL
```

4. Publish the worker:

```powershell
wrangler publish
```

This prints the worker URL (e.g., https://groq-proxy.<your-subdomain>.workers.dev). Point your frontend's API URL to that endpoint.

Notes

- The Worker uses simple retry/backoff for transient network errors.
- Keep GROQ_KEY usage monitored: the Worker avoids exposing the key to the browser.
