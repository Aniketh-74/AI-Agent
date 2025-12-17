"""Clean FastAPI backend: single-file main.py.

This file provides:
- /api/health
- /api/ai
- /api/agents/workflow

It uses GROQ as the LLM provider. The groq_call function includes retry + backoff.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import os
import requests
import time
import random
import logging
from dotenv import load_dotenv

load_dotenv()

# Read GROQ configuration from environment
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_API_URL: str = os.getenv("GROQ_API_URL", "https://api.groq.ai/v1/generate")
# Optional model name; change to your preferred model
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "groq-1")
GROQ_TIMEOUT: int = int(os.getenv("GROQ_TIMEOUT", "30"))
GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "256"))

app = FastAPI(title="AI Agent Backend (GROQ)")

# CORS - allow development hosts and any configured frontend origin via env
# Set ALLOW_ORIGINS environment variable as a comma-separated list to override.
default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    default_origins.append(frontend_url)

env_allow = os.getenv("ALLOW_ORIGINS")
if env_allow:
    # allow comma-separated values
    allow_origins = [o.strip() for o in env_allow.split(",") if o.strip()]
else:
    allow_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("backend")


class PromptRequest(BaseModel):
    prompt: str
    workflow: Optional[str] = None


def choose_workflow_from_prompt(text: str) -> str:
    t = (text or "").lower()
    dev_keywords = [
        "code",
        "function",
        "script",
        "python",
        "javascript",
        "java",
        "implement",
        "unit test",
        "test",
        "api",
        "endpoint",
        "docker",
        "kubernetes",
        "bug",
        "refactor",
        "validate",
        "schema",
        "database",
        "sql",
        "cli",
    ]
    editorial_keywords = [
        "write",
        "draft",
        "email",
        "blog",
        "article",
        "summary",
        "press",
        "copy",
        "landing",
        "headline",
        "marketing",
    ]

    for k in dev_keywords:
        if k in t:
            return "dev"
    for k in editorial_keywords:
        if k in t:
            return "editorial"
    return "editorial"


def groq_call(user_text: str, system_text: Optional[str] = None) -> str:
    # Allow tests to monkeypatch requests.post even when GROQ_API_KEY is not set.
    # In production, missing the key should be considered an operational issue,
    # but for testability we log a warning and proceed so unit tests can mock network calls.
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured; continuing so tests can mock network calls")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    openai_mode = "/openai/" in GROQ_API_URL
    if openai_mode:
        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        messages.append({"role": "user", "content": user_text})
        base_payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": GROQ_MAX_TOKENS,
            "temperature": 0.2,
        }
    else:
        combined = (system_text + "\n\n" if system_text else "") + user_text
        base_payload = {
            "model": GROQ_MODEL,
            "input": combined,
            "max_output_tokens": GROQ_MAX_TOKENS,
            "temperature": 0.2,
        }

    max_retries = 3
    backoff_base = 1.0
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.debug("GROQ request attempt=%s", attempt)
            resp = requests.post(GROQ_API_URL, json=base_payload, headers=headers, timeout=GROQ_TIMEOUT)

            if resp.status_code == 200:
                data = resp.json()
                text = None
                if isinstance(data, dict):
                    if "output" in data:
                        out = data["output"]
                        if isinstance(out, list) and out:
                            text = out[0]
                        elif isinstance(out, str):
                            text = out
                    elif "generations" in data:
                        gens = data["generations"]
                        if isinstance(gens, list) and gens:
                            first = gens[0]
                            text = first.get("text") or first.get("output")
                    elif "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                        c = data["choices"][0]
                        if isinstance(c.get("message"), dict):
                            text = c.get("message", {}).get("content")
                        else:
                            text = c.get("text") or c.get("message")
                    elif "text" in data:
                        text = data.get("text")

                if not text:
                    text = resp.text
                return text

            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                last_err = Exception(f"Transient GROQ error: {resp.status_code} {resp.text}")
                if attempt < max_retries:
                    jitter = random.uniform(0, 0.5)
                    sleep_for = backoff_base * (2 ** (attempt - 1)) + jitter
                    time.sleep(sleep_for)
                    continue
                else:
                    raise last_err

            raise Exception(f"GROQ API error: {resp.status_code} {resp.text}")

        except requests.RequestException as re:
            last_err = re
            if attempt < max_retries:
                jitter = random.uniform(0, 0.5)
                sleep_for = backoff_base * (2 ** (attempt - 1)) + jitter
                time.sleep(sleep_for)
                continue
            else:
                raise

    if last_err:
        raise last_err
    raise Exception("Unknown error in groq_call")


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/ai")
async def ai_endpoint(request: PromptRequest) -> Dict[str, str]:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server")
    try:
        text = groq_call(request.prompt)
        return {"response": (text or "")}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("ai_endpoint error")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/agents/workflow")
async def agent_workflow(request: PromptRequest) -> Dict[str, object]:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server")

    user_prompt = request.prompt
    supplied = (request.workflow or "").strip().lower()

    if supplied and supplied != "auto":
        workflow = supplied
    else:
        workflow = choose_workflow_from_prompt(user_prompt)

    timeline: List[Dict[str, str]] = []

    try:
        if workflow == "editorial":
            planner_system = (
                "You are PlannerAgent. Given the user's request, produce 3 concise subtasks or steps to accomplish it."
            )
            planner_input = f"User request: {user_prompt}\n\nOutput: Provide numbered subtasks with a one-line purpose each."
            planner_out = groq_call(planner_input, planner_system)
            timeline.append({"agent": "Planner", "text": planner_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

            writer_system = (
                "You are WriterAgent. Use the PlannerAgent subtasks and the original request to produce a high-quality deliverable."
            )
            writer_input = f"Original request: {user_prompt}\n\nPlanner subtasks:\n{planner_out}\n\nPlease produce the final output now."
            writer_out = groq_call(writer_input, writer_system)
            timeline.append({"agent": "Writer", "text": writer_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

            reviewer_system = (
                "You are ReviewerAgent. Critique the WriterAgent output for clarity, correctness, and tone; return a short critique and an improved version."
            )
            reviewer_input = f"Writer output:\n{writer_out}\n\nProvide: (1) short critique, (2) an improved version of the output."
            reviewer_out = groq_call(reviewer_input, reviewer_system)
            timeline.append({"agent": "Reviewer", "text": reviewer_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

        elif workflow == "dev":
            researcher_system = (
                "You are ResearcherAgent. For the developer task provided, gather a concise list of facts, best practices, pitfalls, and example resources the CodeWriter should use."
            )
            researcher_input = f"Dev task: {user_prompt}\n\nOutput: Provide bullet points with relevant facts and links (if applicable)."
            researcher_out = groq_call(researcher_input, researcher_system)
            timeline.append({"agent": "Researcher", "text": researcher_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

            codewriter_system = (
                "You are CodeWriterAgent. Produce working, commented code to implement the task. Refer to ResearcherAgent notes when relevant. Return code in a markdown fenced block."
            )
            codewriter_input = f"Task: {user_prompt}\n\nResearch notes:\n{researcher_out}\n\nProduce the implementation now."
            codewriter_out = groq_call(codewriter_input, codewriter_system)
            timeline.append({"agent": "CodeWriter", "text": codewriter_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

            tester_system = (
                "You are TesterAgent. Review the code from CodeWriterAgent, identify bugs or edge-cases, and provide unit tests or validation steps."
            )
            tester_input = f"Code:\n{codewriter_out}\n\nProvide: (1) short review of correctness, (2) unit tests or validation steps."
            tester_out = groq_call(tester_input, tester_system)
            timeline.append({"agent": "Tester", "text": tester_out, "timestamp": datetime.utcnow().isoformat() + "Z"})

        else:
            raise Exception(f"Unknown workflow: {workflow}")

        return {"timeline": timeline, "workflow": workflow}

    except Exception as exc:
        logger.exception("agent_workflow error")
        raise HTTPException(status_code=500, detail=str(exc))
