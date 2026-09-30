# Labs

Exercises for the Local Shop Concierge. Chapters 1–6 are scripts you can run. Chapters 4–10 are assignment labs with starter files. The other chapter folders are stubs.

Do this setup once from the repo root. Then open the lab you are on and follow that README.

## Labs

| Lab | Script |
|---|---|
| [Chapter 1. Hello Concierge](ch01-what-an-agent-is/README.md) | `labs/ch01-what-an-agent-is/hello_concierge.py` |
| [Chapter 2. Your first loop](ch02-your-first-loop/README.md) | `labs/ch02-your-first-loop/file_agent.py` |
| [Chapter 3. Swap the model](ch03-models-without-the-pain/README.md) | `labs/ch03-models-without-the-pain/swap_model.py` |
| [Chapter 4. Tools and sensors](ch04-tools-and-sensors/README.md) | `labs/ch04-tools-and-sensors/stock_agent.py` |
| [Chapter 5. Context engineering](ch05-context-engineering/README.md) | `labs/ch05-context-engineering/restock_notes.py` |
| [Chapter 6. Memory](ch06-memory/README.md) | `labs/ch06-memory/prefs_agent.py` |
| [Chapter 7. Skills](ch07-skills-as-portable-procedures/README.md) | `labs/ch07-skills-as-portable-procedures/concierge.py` |
| [Chapter 8. Browse](ch08-browsing-the-web/README.md) | `labs/ch08-browsing-the-web/browse_agent.py` |
| [Chapter 9. Protocols](ch09-protocols-and-open-stack/README.md) | `labs/ch09-protocols-and-open-stack/concierge.py` |
| [Chapter 10. Runtime](ch10-runtime-for-long-running-agents/README.md) | `labs/ch10-runtime-for-long-running-agents/restock.py` |

Each of Labs 1–3 has a `SOLUTION.md` in its folder. Those notes are for instructors and for checking your own write-up after you have finished it. If the lab is homework, finish the write-up before you open that file. Labs 4–10 do not include a solution file. Follow the assignment in that lab's README. The starter scripts are incomplete on purpose.

## Requirements

- Python 3.10 or newer
- An OpenAI API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

The labs share one client, `labs/common/client.py`. It uses the official OpenAI Python SDK and the default API (`https://api.openai.com/v1`). You do not set a base URL.

Chapter 1 is a single chat completion. Tool calling is not required. Chapters 2–6 need a model that can emit tool calls. The default `gpt-4.1-mini` does. If a trace never shows a tool call, set `MODEL` to another current tool-capable id, such as `gpt-4.1`.

## Install

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

## Configure `.env`

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` is gitignored. `.env.example` is the committed template. Do not commit a real key.

| Variable | Meaning | Default |
|---|---|---|
| `OPENAI_API_KEY` | Secret from platform.openai.com. Required. | none (the process exits) |
| `MODEL` | Model id the API expects. Optional. | `gpt-4.1-mini` |

`gpt-4.1-mini` supports tool calling, which Chapters 2 and 3 need. The id is documented at [developers.openai.com/api/docs/models/gpt-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini). If that page says the id has changed, put the current tool-capable id in `MODEL`.

Process environment variables win over `.env`. An empty `OPENAI_API_KEY` exits before the request. A blank `MODEL` uses `gpt-4.1-mini`.

A request includes the prompt and, once a loop is running, the tool results. Chapters 2 and 3 send shop documents. Chapters 4–6 can send shelf rows, note bodies, and memory records. The café material in this repo is fictional. Do not point the loop at a private document.

## Run each script

From the repo root, with the virtualenv active:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
python labs/ch02-your-first-loop/file_agent.py
python labs/ch03-models-without-the-pain/swap_model.py
python labs/ch04-tools-and-sensors/stock_agent.py
python labs/ch05-context-engineering/restock_notes.py
python labs/ch06-memory/prefs_agent.py
```

Each script prints `MODEL` and hides the key. Optional questions are extra arguments. Chapter 3 is the Chapter 2 loop. Switching models is an edit to `MODEL` in `.env`, then the same command. Shop files are `labs/ch02-your-first-loop/docs/policy.md` and `docs/faq.md`.

Chapter 4 rebuilds a SQLite shelf and answers "What's low stock?" `python labs/ch04-tools-and-sensors/stock_agent.py --check` exercises the SQL tools without a model. Chapter 5 defaults to filing notes (`file`); `size` prints the context budget without a model, and `next` asks the morning question. Chapter 6 stores guest memory in JSON. `--check` and `--reset` do not call a model; `quiz` is the next process.

Chapters 7–10 follow the lab README in each folder. Chapter 9's contract test does not need a model. Chapter 10's ledger check does not need one either.

## Check the harness without a model

```bash
python -m unittest labs.common.test_harness
```

That covers the docs path jail, tool-error handling, max steps, and the repeated-call stop. It does not call the OpenAI API.

## Troubleshooting

A request error means `.env` or the key, not the café prompt. The key is not printed. A header line `OPENAI_API_KEY=set (value hidden)` means a non-empty value was loaded. `OPENAI_API_KEY=missing (value hidden)` means it was not.

- **`OPENAI_API_KEY` is empty.** Copy `.env.example` to `.env` and paste a key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys). The process exits before the request.
- **HTTP 401.** The key is wrong, revoked, or still a placeholder.
- **HTTP 404 on the model.** `MODEL` is stale or not enabled on your account. Change `MODEL` only. `gpt-4.1-mini` and `gpt-4.1` are the ids these labs use.
- **Connection error.** Check the network. The client talks to `https://api.openai.com/v1`. There is no local server to start.
- **Empty tool log on Chapters 2–6, with `final` after 1 model call.** The API answered and the model never called the tool. Set `MODEL` to another tool-capable id (for example `gpt-4.1`) and run again. Do not change the question.
- **An older `.env` still has `BASE_URL` and `API_KEY`.** This client ignores those names. Set `OPENAI_API_KEY` and, if you want, `MODEL`.
