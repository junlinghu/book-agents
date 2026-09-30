# Local Shop Concierge tutorial

Fifteen notebooks that build one shop agent for the fictional Hearth Lane Café. Each lesson keeps the previous agent's code, then adds one idea from the book. You can run a notebook by itself.

This folder uses the same OpenAI client as the other labs (`labs/common/client.py`). Shop policy and FAQ text come from `labs/ch02-your-first-loop/docs/`. The shelf rows match Chapter 4.

## Status

| # | Notebook | Summary | Status |
|---|---|---|---|
| 1 | [1-using-tool](1-using-tool.ipynb) | Define a tool, let the model request it, run it, and send the result back. | Ready |
| 2 | [2-data-and-files](2-data-and-files.ipynb) | Tools that read shop documents and the SQLite shelf. | Ready |
| 3 | [3-agent-loop](3-agent-loop.ipynb) | Perceive–reason–act–observe, with step and repeat stops. | Ready |
| 4 | [4-context-engineering](4-context-engineering.ipynb) | Note titles in the prompt; bodies loaded on purpose. | Ready |
| 5 | [5-memory](5-memory.ipynb) | Session messages versus a JSON memory file. | Ready |
| 6 | [6-skills](6-skills.ipynb) | A procedure file, separate from the system prompt and the tools. | Ready |
| 7 | [7-web-browse](7-web-browse.ipynb) | One supplier page, treated as an untrusted sensor. | Ready |
| 8 | [8-verification](8-verification.ipynb) | A checker that does not trust the proposed quantity. | Ready |
| 9 | [9-evals](9-evals.ipynb) | A tiny grader, including one canned failure. | Ready |
| 10 | [10-autonomy-policy](10-autonomy-policy.ipynb) | Auto, confirm, and never gates. | Ready |
| 11 | [11-prompt-injection](11-prompt-injection.ipynb) | Untrusted page text cannot grant tools or reveal a canary. | Ready |
| 12 | 12-multi-agent | A stocker and a checker hand off a shelf gap, not a note's quantity. | Planned |
| 13 | 13-observability | Spans that name the user, the agent, and the tool. | Planned |
| 14 | 14-cost-latency | Token, cost, and latency ledger, plus a read cache. | Planned |
| 15 | 15-shop-manager | Tuesday restock: plan, check, confirm, write tickets. | Planned |

Planned rows are the later lessons in this series. They are not in this folder until that lesson is merged.

## Prerequisites

- Python 3.10 or newer
- A virtualenv and the repo requirements
- For a live model call: an OpenAI API key

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Put the key in `OPENAI_API_KEY` inside the repo-root `.env`. `MODEL` is optional. Blank uses `gpt-4.1-mini`. Do not commit `.env`.

`requirements.txt` installs `openai`, `python-dotenv`, `httpx`, and, for these notebooks, `jupyter`, `ipykernel`, and `nbformat`.

## How to open a notebook

Start Jupyter from the repo root, or open the `.ipynb` in VS Code or Cursor and choose Run All.

```bash
jupyter notebook labs/tutorial/1-using-tool.ipynb
```

The setup cell looks for `labs/common/client.py` in the current directory and its parents. The kernel can start in the repo root or in `labs/tutorial/`.

Each lesson has a companion note, `N-slug.md`, with the purpose, what to learn, the chapter map, and run commands.

## DEMO_MODE and the live API

The first code cell of each notebook sets `DEMO_MODE`.

| Value | What runs |
|---|---|
| `None` (the default in the notebook) | If the environment variable `DEMO_MODE` is `1`, `true`, `yes`, or `on`, the scripted demo runs. If it is `0`, `false`, `no`, or `off`, the notebook calls the API. If the variable is unset, a missing `OPENAI_API_KEY` selects the demo and a present key selects the API. |
| `True` | Scripted demo, even when a key is set. No network call. |
| `False` | Chat Completions API. The run stops with a clear error if the key is empty. |

```bash
DEMO_MODE=1 jupyter nbconvert --to notebook --execute labs/tutorial/1-using-tool.ipynb --output /tmp/1-using-tool-out.ipynb
```

`DEMO_MODE=0` is the live path. Temperature and max tokens come from `labs/common/client.py`, same as the other labs.

In demo mode the tools, the loop, the checker, and the gates are the real functions. Only the model turn is scripted, so the printed trace is stable without an API key. A live model can phrase the answer differently. Demo checks raise when the scripted trace drifts. Live runs print a warning and continue.

The script does not print the API key.

## Shared pieces

| Path | Role |
|---|---|
| `runtime.py` | Loads `.env` through `labs/common/client.py` and exposes `chat`. |
| `demo_model.py` | Scripted tool-calling turns for `DEMO_MODE`. |
| `data/` | Notes, skills, the supplier page, the supplier note, and a fake canary. Not shop secrets. |
| `cell_src/` | Authoring copy of the cells. Notebooks inline this code so each file still runs alone. |
| `build_series.py` | Rewrites the notebooks and companion notes from `cell_src/`. You do not need it to study. |
| `labs/common/client.py` | API key, model, temperature, max tokens. |
| `labs/common/tools.py` | Path jail used by `read_shop_file`. |
| `labs/common/autonomy.py` | Confirm tokens, and the never-tier for cards and outside mail. |

Runtime files under `labs/tutorial/var/` (memory JSON and tickets) are gitignored.

## Rebuild

From the repo root, after editing `cell_src/`:

```bash
python labs/tutorial/build_series.py
DEMO_MODE=1 python labs/tutorial/build_series.py --check
```

`--check` executes every notebook's code cells in the scripted demo. It does not call the API.
