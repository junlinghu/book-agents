# Introduction to AI Agents

The spine agent is a Local Shop Concierge for a café / small store. The same bot grows every chapter.

Runtime is desktop-first (Ollama or Groq), with SQLite, markdown docs, and a tiny shop site in the repo.

Framing: Agent quality = Model × Harness × Feedback loop.

Repository: https://github.com/junlinghu/book-agents

## Folders

- `chapters/` — narrative outline per chapter.
- `labs/` — code lab stubs (filled in later), one folder per chapter.

## Outline

### Part I — Foundations

- [Ch 1. What an agent is (builders' cut)](chapters/ch01-what-an-agent-is/README.md) — Hello Concierge—single completion, no tools; list three failure modes you saw
- [Ch 2. Your first loop](chapters/ch02-your-first-loop/README.md) — Wire `read_file`; answer return/shipping questions from `policy.md` / `faq.md` with path citations
- [Ch 3. Models without the pain](chapters/ch03-models-without-the-pain/README.md) — Run the Ch 2 agent on Ollama and Groq (or OpenRouter) by editing `.env` only

### Part II — Harness

- [Ch 4. Tools and sensors](chapters/ch04-tools-and-sensors/README.md) — SQLite `products`, `inventory`; `sql_query` / limited `sql_execute`; "what's low stock?"
- [Ch 5. Context engineering](chapters/ch05-context-engineering/README.md) — Long restock dialogue; write `notes/`; reload selective notes next turn
- [Ch 6. Memory](chapters/ch06-memory/README.md) — Persist café prefs across process restarts; adversarial quiz next "day"
- [Ch 7. Skills as portable procedures](chapters/ch07-skills-as-portable-procedures/README.md) — Add `skills/recommend.md` and `skills/cite-sources.md`; change behavior by editing markdown
- [Ch 8. Browsing the web](chapters/ch08-browsing-the-web/README.md) — Fetch your static shop page (or one public product page); compare to SQLite price
- [Ch 9. Protocols and the open agent stack](chapters/ch09-protocols-and-open-stack/README.md) — Expose SQL + fetch as MCP servers; Concierge uses MCP only
- [Ch 10. Runtime for long-running agents](chapters/ch10-runtime-for-long-running-agents/README.md) — Multi-step restock; kill mid-run; resume from checkpoint without double-ordering

### Part III — Feedback loop

- [Ch 11. Verification loops](chapters/ch11-verification-loops/README.md) — Recommender proposes cart; Checker rejects missing citations / nut allergies / over budget
- [Ch 12. Evals from real failures](chapters/ch12-evals-from-real-failures/README.md) — Turn 10 logged failures into fixtures; game a weak grader; harden it
- [Ch 13. Simulated users and environments](chapters/ch13-simulated-users-and-environments/README.md) — CI job runs three personas; assert cart constraints and no forbidden actions
- [Ch 14. Production signals and honest metrics](chapters/ch14-production-signals-and-honest-metrics/README.md) — Log success/confirm/cost/latency; build a one-page metrics report for Concierge
- [Ch 15. Pulling the model lever (lightly)](chapters/ch15-pulling-the-model-lever/README.md) — Collect preference pairs; run a controlled bake-off (skill update vs larger model)—no cluster required

### Part IV — Autonomy, products, domains

- [Ch 16. Autonomy policy](chapters/ch16-autonomy-policy/README.md) — Auto price-check; confirm `place_order`; never `charge_card` / email external
- [Ch 17. Work-agent blueprint](chapters/ch17-work-agent-blueprint/README.md) — Add draft-email (or draft-calendar) tool; send only after confirm
- [Ch 18. Agentic commerce](chapters/ch18-agentic-commerce/README.md) — End-to-end mock checkout → `orders` row; no live payments
- [Ch 19. Customer support agent](chapters/ch19-customer-support-agent/README.md) — `tickets` table + policy PDF/md; draft reply with citations; human approve
- [Ch 20. Financial-flavored prudence](chapters/ch20-financial-flavored-prudence/README.md) — Daily sales summary from DB; dual-approve mock `refund`

### Part V — Security, multi-agent, ops

- [Ch 21. Prompt injection and untrusted data](chapters/ch21-prompt-injection-and-untrusted-data/README.md) — Poison competitor HTML; Concierge must not leak `.env` or email secrets
- [Ch 22. Identity and observability](chapters/ch22-identity-and-observability/README.md) — OpenTelemetry-style trace per restock; replay one failure from logs alone
- [Ch 23. Multi-agent patterns](chapters/ch23-multi-agent-patterns/README.md) — Researcher + Buyer + Checker with explicit I/O contracts
- [Ch 24. Cost, latency, and architecture](chapters/ch24-cost-latency-and-architecture/README.md) — A/B router; report $ and wall-clock for the same restock scenario
- [Ch 25. Self-improving agents (honestly)](chapters/ch25-self-improving-agents/README.md) — Agent proposes a skill patch; merge only if Ch 12 suite stays green

### Part VI — Capstone and outlook

- [Ch 26. Capstone: café restock end-to-end](chapters/ch26-capstone-cafe-restock/README.md) — One recorded end-to-end run: files + DB + web + memory + confirm order + ticket if OOS + green evals
- [Ch 27. Open problems](chapters/ch27-open-problems/README.md) — One-page "known limitations" for your Concierge + three experiments you'd run next

### Appendices

- [Appendix A. Setup](chapters/appendix-a-setup/README.md) — Clone, install, seed DB, run Hello Concierge once
- [Appendix B. Models cheat sheet](chapters/appendix-b-models-cheat-sheet/README.md) — Switch providers via `.env` and confirm tool calling still works
- [Appendix C. Source map](chapters/appendix-c-source-map/README.md) — Add a dated source stub file for three chapters of your choice
- [Appendix D. Safety & ToS](chapters/appendix-d-safety-and-tos/README.md) — Fill a safety checklist for the Ch 8 browse lab before running it
- [Appendix E. Glossary](chapters/appendix-e-glossary/README.md) — Write one-sentence definitions in your own words for each glossary term
