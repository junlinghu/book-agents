# Introduction to AI Agents

The spine agent is a Local Shop Concierge for a café / small store. The same bot grows every chapter.

Runtime is desktop-first (Ollama, Groq, or OpenRouter), with SQLite, markdown docs, and a tiny shop site in the repo.

Framing: Agent quality = Model × Harness × Feedback loop.

Repository: https://github.com/junlinghu/book-agents

## Folders

- `chapters/` — manuscript. Chapters 1–3 are full prose. Later chapters are still outlines.
- `labs/` — Chapters 1–3 are runnable. Later labs are stubs.

## Running the labs

This section is the shared setup for Chapters 1–3. Each lab README repeats what that lab needs (goal, install, `.env`, the command, what to observe, troubleshooting) and is the operational guide for that chapter. The commands here and in the lab READMEs are the same.

Chapters 1–3 share one OpenAI-compatible client. Ollama is the default. Groq and OpenRouter are the same three variables in `.env`.

### Requirements

- Python 3.10 or newer
- Either **Ollama** on your machine, or an API key for **Groq** or **OpenRouter**

Chapter 1 is a single chat completion. Chapters 2 and 3 need a model that can emit tool calls.

### Install

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`requirements.txt` installs `openai`, `python-dotenv`, and `httpx`.

### Configure `.env`

```bash
cp .env.example .env
```

`.env` is gitignored. `.env.example` is the committed template. Do not commit a real hosted key.

| Variable | Meaning | Ollama default |
|---|---|---|
| `BASE_URL` | OpenAI-compatible API origin | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama ignores the value and still wants a non-empty string. | `ollama` |
| `MODEL` | Model name that server expects | `llama3.2` |

Process environment variables win over `.env`. Commented Groq and OpenRouter blocks are in `.env.example`. Use one provider at a time.

### Ollama

Install from [ollama.com/download](https://ollama.com/download), pull the default tag, and start the server if it is not already running:

```bash
ollama pull llama3.2
ollama serve
```

Default `.env`:

```env
BASE_URL=http://localhost:11434/v1
API_KEY=ollama
MODEL=llama3.2
```

If Chapter 2's trace never shows a `read_file` call, pull a tool-capable fallback and change only `MODEL`:

```bash
ollama pull llama3.1
```

```env
MODEL=llama3.1
```

### Groq or OpenRouter

Comment out the Ollama lines in `.env` and set one hosted provider. These placeholders are not real keys:

```env
# Groq — use a model with local tool-call support, not groq/compound
BASE_URL=https://api.groq.com/openai/v1
API_KEY=gsk_your_key_here
MODEL=llama-3.3-70b-versatile
```

```env
# OpenRouter — confirm the id on the model page and that it lists tools
BASE_URL=https://openrouter.ai/api/v1
API_KEY=sk-or-your_key_here
MODEL=meta-llama/llama-3.3-70b-instruct
```

A hosted request includes the prompt and, for Chapters 2 and 3, the text of any file the agent read. The shop docs are fictional. Do not send a private document to a third-party API unless you mean to.

### Run each script

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
python labs/ch02-your-first-loop/file_agent.py
python labs/ch03-models-without-the-pain/swap_model.py
```

Each script prints `BASE_URL` and `MODEL` and hides the key. Optional questions are extra arguments:

```bash
python labs/ch02-your-first-loop/file_agent.py "What's the Wi-Fi password?"
python labs/ch03-models-without-the-pain/swap_model.py "How much is local delivery, and which day are you closed?"
```

Chapter 3 is the Chapter 2 loop. Switching providers is an edit to `.env`, then the same command. Shop files are `labs/ch02-your-first-loop/docs/policy.md` and `docs/faq.md`. Per-lab notes:

- `labs/ch01-what-an-agent-is/README.md` — failure modes to write down
- `labs/ch02-your-first-loop/README.md` — docs, stop conditions, citations
- `labs/ch03-models-without-the-pain/README.md` — Ollama vs Groq vs OpenRouter

### Check the harness without a model

```bash
python -m unittest labs.common.test_harness
```

That covers the docs path jail, tool-error handling, max steps, and the repeated-call stop. It does not contact Ollama or a hosted API.

## Outline

### Part I — Foundations

1. [What an agent is](chapters/ch01-what-an-agent-is/README.md)

   Chatbots, workflows, and agents, and the Model × Harness × Feedback framing for practitioners and product managers.

2. [Your first loop](chapters/ch02-your-first-loop/README.md)

   The perceive–reason–act–observe loop, tool schemas, stop conditions, and what a trace should show.

3. [Models without the pain](chapters/ch03-models-without-the-pain/README.md)

   Hosted APIs versus local weights, and swapping models through a stable OpenAI-compatible client while the harness stays fixed.

### Part II — Harness

4. [Tools and sensors](chapters/ch04-tools-and-sensors/README.md)

   Tools as the model's sensors and actuators, with safe boundaries and errors it can recover from.

5. [Context engineering](chapters/ch05-context-engineering/README.md)

   Context windows, context rot, and budgets for what enters the prompt.

6. [Memory](chapters/ch06-memory/README.md)

   Session versus durable memory: preferences, stale beliefs, and how to forget.

7. [Skills as portable procedures](chapters/ch07-skills-as-portable-procedures/README.md)

   Skills as portable, versioned procedures, separate from tools and the system prompt.

8. [Browsing the web](chapters/ch08-browsing-the-web/README.md)

   Fetching the web as an untrusted sensor, with grounding, terms of service, and PII hygiene.

9. [Protocols and the open agent stack](chapters/ch09-protocols-and-open-stack/README.md)

   MCP, A2A, and contract tests: protocols that let the harness outlive one vendor.

10. [Runtime for long-running agents](chapters/ch10-runtime-for-long-running-agents/README.md)

    Checkpoints, sandboxing, and a runtime for work that outlasts one context window.

### Part III — Feedback loop

11. [Verification loops](chapters/ch11-verification-loops/README.md)

    A separate checker for policy, citations, and constraints, with human review as a tier.

12. [Evals from real failures](chapters/ch12-evals-from-real-failures/README.md)

    Evals built from real failures, and graders that themselves must be hardened.

13. [Simulated users and environments](chapters/ch13-simulated-users-and-environments/README.md)

    Persona scripts and simulated clocks, inventory, and stockouts for repeatable tests.

14. [Production signals and honest metrics](chapters/ch14-production-signals-and-honest-metrics/README.md)

    Production signals for finished work: success, confirms, cost, and latency.

15. [Pulling the model lever (lightly)](chapters/ch15-pulling-the-model-lever/README.md)

    When to change the model versus the harness, and how to measure which lever moved the metric.

### Part IV — Autonomy, products, domains

16. [Autonomy policy](chapters/ch16-autonomy-policy/README.md)

    Autonomy tiers (auto, confirm, and never) mapped to action risk.

17. [Work-agent blueprint](chapters/ch17-work-agent-blueprint/README.md)

    The shared work-agent blueprint of files, browser, memory, tools, and approvals.

18. [Agentic commerce](chapters/ch18-agentic-commerce/README.md)

    Catalog, cart, and checkout for commerce agents, including inventory truth and the trust gap.

19. [Customer support agent](chapters/ch19-customer-support-agent/README.md)

    Customer support as the same loop: tickets, policy-grounded answers, and escalation.

20. [Financial-flavored prudence](chapters/ch20-financial-flavored-prudence/README.md)

    Audit trails, dual control, and read-mostly defaults for money-adjacent actions.

### Part V — Security, multi-agent, ops

21. [Prompt injection and untrusted data](chapters/ch21-prompt-injection-and-untrusted-data/README.md)

    Indirect prompt injection through untrusted text, and boundaries that keep secrets out of the model.

22. [Identity and observability](chapters/ch22-identity-and-observability/README.md)

    Identity of user, agent, and tool, plus traces you can replay.

23. [Multi-agent patterns](chapters/ch23-multi-agent-patterns/README.md)

    Constrained multi-agent roles and handoffs, and when one agent is enough.

24. [Cost, latency, and architecture](chapters/ch24-cost-latency-and-architecture/README.md)

    Cost and latency of a finished task, and routing and caching as architecture levers.

25. [Self-improving agents (honestly)](chapters/ch25-self-improving-agents/README.md)

    Self-improvement limited to safe surfaces, gated by evals and human merges.

### Part VI — Capstone and outlook

26. [Capstone: café restock end-to-end](chapters/ch26-capstone-cafe-restock/README.md)

    One café restock that composes the full harness, checks, and metrics.

27. [Open problems](chapters/ch27-open-problems/README.md)

    Stale harness assumptions, grader gaming, long-horizon reliability, and commerce trust.

### Appendices

1. [Appendix A. Setup](chapters/appendix-a-setup/README.md)

   Desktop and Codespaces setup, repo layout, and seeding the shop database.

2. [Appendix B. Models cheat sheet](chapters/appendix-b-models-cheat-sheet/README.md)

   A provider cheat sheet for local and hosted models, including tool-calling notes.

3. [Appendix C. Source map](chapters/appendix-c-source-map/README.md)

   A dated map from chapters to sources and further reading.

4. [Appendix D. Safety & ToS](chapters/appendix-d-safety-and-tos/README.md)

   Safety and terms-of-service rules for public web, PII, and payments.

5. [Appendix E. Glossary](chapters/appendix-e-glossary/README.md)

   Shared definitions for harness, skill, MCP, grader, autonomy tier, and context rot.
