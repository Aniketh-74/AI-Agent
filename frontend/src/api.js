import axios from "axios";

// Configure a shared axios instance with sensible defaults
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const client = axios.create({
  baseURL: API_URL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

async function handleResponse(promise) {
  try {
    const res = await promise;
    return res.data;
  } catch (err) {
    // Normalize errors so frontend can display them consistently
    if (err.response && err.response.data) {
      throw new Error(err.response.data.detail || JSON.stringify(err.response.data));
    }
    throw err;
  }
}

export function callAI(prompt) {
  return handleResponse(client.post("/api/ai", { prompt }));
}

export function runAgentWorkflow(prompt, workflow = "editorial") {
  // send workflow param to the backend so it can pick the correct agent chain
  return handleResponse(client.post("/api/agents/workflow", { prompt, workflow }));
}
