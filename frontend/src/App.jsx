import React, { useState } from "react";
import { callAI, runAgentWorkflow } from "./api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import "./styles.css";

const WORKFLOWS = [
  { key: "editorial", label: "Editorial (Planner→Writer→Reviewer)" },
  { key: "dev", label: "Dev (Researcher→CodeWriter→Tester)" },
];

export default function App() {
  const [prompt, setPrompt] = useState(
    "Give me a short, professional greeting"
  );
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [agentTimeline, setAgentTimeline] = useState([]);
  const [workflowRunning, setWorkflowRunning] = useState(false);
  const [copyStatus, setCopyStatus] = useState({});

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResponse("");
    try {
      const res = await callAI(prompt);
      setResponse(res.response);
    } catch (err) {
      setResponse("Error: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  }

  

  const [selectedWorkflow, setSelectedWorkflow] = useState(WORKFLOWS[0].key);

  async function runWorkflow(e, wf = null) {
    e && e.preventDefault();
    setWorkflowRunning(true);
    setAgentTimeline([]);
    try {
      const workflowToUse = wf || selectedWorkflow;
      const data = await runAgentWorkflow(prompt, workflowToUse);
      // attach timestamps and collapsed state to each entry
      const now = new Date().toISOString();
      const enriched = (data.timeline || []).map((t) => ({
        ...t,
        ts: now,
        expanded: false,
      }));
      setAgentTimeline(enriched);
    } catch (err) {
      setAgentTimeline([
        {
          agent: "System",
          text: "Error: " + (err.message || String(err)),
          ts: new Date().toISOString(),
          expanded: true,
        },
      ]);
    } finally {
      setWorkflowRunning(false);
    }
  }

  // Demo sequence runs a few example tasks to showcase agent-to-agent handoffs
  async function runDemo(e) {
    e && e.preventDefault();
    setAgentTimeline([]);
    setWorkflowRunning(true);
    const demoTasks = [
      {
        prompt:
          "Create an onboarding email for a new user of our product named Acme CRM",
        workflow: "editorial",
      },
      {
        prompt:
          "Write a Python function that validates email addresses and include unit tests",
        workflow: "dev",
      },
      {
        prompt:
          "Draft a short product features summary for Acme CRM landing page",
        workflow: "editorial",
      },
    ];

    try {
      for (const task of demoTasks) {
        const resp = await runAgentWorkflow(task.prompt, task.workflow);
        // annotate each timeline entry with the task title for grouping and add metadata
        const header = {
          agent: "Task",
          text: `Task: ${task.prompt} (workflow: ${task.workflow})`,
          ts: new Date().toISOString(),
          expanded: true,
        };
        const now = new Date().toISOString();
        const enriched = (resp.timeline || []).map((t) => ({
          ...t,
          ts: now,
          expanded: false,
        }));
        setAgentTimeline((prev) => [...prev, header, ...enriched]);
        // small delay so UI updates in a visible way
        await new Promise((r) => setTimeout(r, 300));
      }
    } catch (err) {
      setAgentTimeline((prev) => [
        ...prev,
        { agent: "System", text: "Error during demo: " + (err.message || String(err)) },
      ]);
    } finally {
      setWorkflowRunning(false);
    }
  }

  return (
    <div className="container">
      <header className="app-header">
        <div className="title-row">
          <div className="logo-wrap" aria-hidden>
            <svg className="react-logo" viewBox="0 0 841.9 595.3" xmlns="http://www.w3.org/2000/svg">
              <g fill="none" stroke="#61DAFB" strokeWidth="16">
                <ellipse cx="420.9" cy="296.5" rx="211" ry="86.2"/>
                <ellipse cx="420.9" cy="296.5" rx="211" ry="86.2" transform="rotate(60 420.9 296.5)"/>
                <ellipse cx="420.9" cy="296.5" rx="211" ry="86.2" transform="rotate(120 420.9 296.5)"/>
              </g>
              <circle cx="420.9" cy="296.5" r="45.7" fill="#61DAFB"/>
            </svg>
          </div>
          <div>
            <h1>AI Agent <span className="react-pill">React</span></h1>
            <p className="subtitle">Multi-agent demo — Planner, Writer, Reviewer or Researcher, CodeWriter, Tester</p>
          </div>
        </div>
      </header>

      <form className="prompt-form" onSubmit={onSubmit}>
        
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={6}
          aria-label="Prompt"
        />

        <div className="form-actions">
          <button className="primary" type="submit" disabled={loading}>
            {loading && <span className="btn-spinner" aria-hidden></span>}
            {loading ? "Thinking..." : "Ask AI"}
          </button>
          <div className="spacer" />
          <select
            value={selectedWorkflow}
            onChange={(e) => setSelectedWorkflow(e.target.value)}
          >
            {WORKFLOWS.map((w) => (
              <option key={w.key} value={w.key}>
                {w.label}
              </option>
            ))}
          </select>
          <button className="secondary" onClick={runWorkflow} disabled={workflowRunning}>
            {workflowRunning && <span className="btn-spinner small" aria-hidden></span>}
            {workflowRunning ? "Running…" : "Run workflow"}
          </button>
          <button className="secondary" onClick={runDemo} disabled={workflowRunning}>
            {workflowRunning && <span className="btn-spinner small" aria-hidden></span>}
            {workflowRunning ? "Running demo…" : "Run demo"}
          </button>
        </div>
      </form>

      

      <section className="response">
        <h2>Response</h2>
        <pre>{response}</pre>
      </section>

      <section className="response">
        <h2>Agent timeline</h2>
        {agentTimeline.length === 0 && (
          <p>
            <em>No agent output yet — run the workflow to generate a timeline.</em>
          </p>
        )}

        {agentTimeline.map((t, i) => (
          <div key={i} className="agent-entry">
            <div className="meta">
              <div className="left">
                <div className="agent-badge">{'<' + t.agent + ' />'}</div>
                <div>
                  <div style={{ fontWeight: 700 }}>{t.agent}</div>
                  <div className="ts">{new Date(t.ts).toLocaleString()}</div>
                </div>
              </div>

              <div className="right">
                <button
                  className="small"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(t.text);
                      setCopyStatus((s) => ({ ...s, [i]: "Copied" }));
                      setTimeout(() => setCopyStatus((s) => ({ ...s, [i]: undefined })), 1500);
                    } catch (e) {
                      setCopyStatus((s) => ({ ...s, [i]: "Failed" }));
                    }
                  }}
                >
                  {copyStatus[i] || "Copy"}
                </button>
                <button
                  className="small"
                  onClick={() =>
                    setAgentTimeline((prev) => prev.map((entry, idx) => (idx === i ? { ...entry, expanded: !entry.expanded } : entry)))
                  }
                >
                  {t.expanded ? "Collapse" : "Expand"}
                </button>
              </div>
            </div>

            <div className="body">
              {t.expanded ? (
                <div className="markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
                    {t.text}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="preview">{t.text.length > 300 ? t.text.slice(0, 300) + "…" : t.text}</div>
              )}
            </div>
          </div>
        ))}
      </section>

      <footer>
        <small>Frontend calls backend at VITE_API_URL (set at build/dev). See README.</small>
      </footer>
    </div>
  );
}
