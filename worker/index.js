// Simple Cloudflare Worker proxy for GROQ API
// - Keeps GROQ_API_KEY secret in Worker secrets
// - Exposes two endpoints: /api/ai and /api/agents/workflow
// - Adds CORS headers so the static frontend can call it

addEventListener("fetch", (event) => {
  event.respondWith(handleRequest(event.request));
});

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

async function handleRequest(request) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  const url = new URL(request.url);
  // Only proxy expected API paths
  if (!url.pathname.startsWith("/api/")) {
    return new Response("Not found", { status: 404, headers: CORS_HEADERS });
  }

  // Read incoming JSON (if any)
  let body = null;
  try {
    body = await request.json();
  } catch (err) {
    body = {};
  }

  const groqUrl =
    (typeof GROQ_API_URL !== "undefined" && GROQ_API_URL) ||
    "https://api.groq.ai/v1/generate";
  const groqKey = (typeof GROQ_API_KEY !== "undefined" && GROQ_API_KEY) || "";
  const groqModel =
    (typeof GROQ_MODEL !== "undefined" && GROQ_MODEL) || "groq-1";

  if (!groqKey) {
    return new Response(
      JSON.stringify({
        error: "GROQ_API_KEY not configured in Worker secrets",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json", ...CORS_HEADERS },
      }
    );
  }

  const input = body.prompt || body.input || "";
  const payload = {
    model: groqModel,
    input: input,
    max_output_tokens: 128,
    temperature: 0.2,
  };

  // Forward the request to GROQ with simple retry
  let lastErr;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const resp = await fetch(groqUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${groqKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const text = await resp.text();
      const headers = { "Content-Type": "application/json", ...CORS_HEADERS };
      return new Response(text, { status: resp.status, headers });
    } catch (err) {
      lastErr = err;
      // small backoff
      await new Promise((r) => setTimeout(r, 300 * attempt));
    }
  }

  return new Response(
    JSON.stringify({ error: "Upstream error", details: String(lastErr) }),
    {
      status: 502,
      headers: { "Content-Type": "application/json", ...CORS_HEADERS },
    }
  );
}
