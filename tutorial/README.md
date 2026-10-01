# Local Shop Concierge tutorial

Fifteen notebooks that build one shop agent for the fictional Hearth Lane Café. Each lesson keeps the previous agent's code, then adds one idea from the book. You can run a notebook by itself.

This folder carries its own OpenAI client (`common/client.py`), shop policy and FAQ (`docs/`), path jail (`common/tools.py`), and autonomy gate (`common/autonomy.py`). The shelf rows are seeded in `cell_src/shelf.py`. Nothing here imports a file outside `tutorial/`.

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
| 12 | [12-multi-agent](12-multi-agent.ipynb) | A stocker and a checker hand off a shelf gap, not a note's quantity. | Ready |
| 13 | [13-observability](13-observability.ipynb) | Spans that name the user, the agent, and the tool. | Ready |
| 14 | [14-cost-latency](14-cost-latency.ipynb) | Token, cost, and latency ledger, plus a read cache. | Ready |
| 15 | [15-shop-manager](15-shop-manager.ipynb) | Tuesday restock: plan, check, confirm, write tickets. | Ready |

Every row in the table is ready. Run the notebooks in order, or open any one on its own. Each file still contains the earlier lessons' code.

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
jupyter notebook tutorial/1-using-tool.ipynb
```

The setup cell looks for `tutorial/common/client.py` in the current directory and its parents. The kernel can start in the repo root or in `tutorial/`.

To run a notebook on Google Colab instead, use the **Open in Colab** badge at the top of the file. See [Open in Colab](#open-in-colab).

Each lesson has a companion note, `N-slug.md`, that places the lesson on the path from a single tool to the shop manager and points to the matching chapter. How to run a notebook is in the sections above.

## Open in Colab

Each notebook has an **Open in Colab** badge at the top. The badge opens that file on Google Colab from the `main` branch:

```text
https://colab.research.google.com/github/junlinghu/book-agents/blob/main/tutorial/<notebook>.ipynb
```

Tutorial 1, for example, is [1-using-tool.ipynb](https://colab.research.google.com/github/junlinghu/book-agents/blob/main/tutorial/1-using-tool.ipynb).

Run the Colab setup cell first (it is the first code cell). On Colab that cell:

- Detects Colab (`google.colab` and a `/content` directory).
- Sparse-checkouts the public repository so `tutorial/` is on disk (`tutorial.common`, `docs/`, and the rest of the lesson). If the sparse checkout fails, it falls back to a shallow clone.
- Installs `openai`, `python-dotenv`, and `httpx` when those imports are missing.
- Sets the working directory and `sys.path` so `import tutorial` works.

The same cell runs in local Jupyter and VS Code and skips the clone and the install. A checkout you already have does not need another clone.

Edits you make in Colab stay in the Colab session. They do not push to GitHub.

`DEMO_MODE` still runs the scripted lesson when `OPENAI_API_KEY` is unset. For a live call, add a Colab secret named `OPENAI_API_KEY` (the key icon), or set `os.environ["OPENAI_API_KEY"]` in a cell before the lesson setup cell that assigns `DEMO_MODE`. The notebooks do not print the key.

## DEMO_MODE and the live API

The first code cell of each notebook sets `DEMO_MODE`.

| Value | What runs |
|---|---|
| `None` (the default in the notebook) | If the environment variable `DEMO_MODE` is `1`, `true`, `yes`, or `on`, the scripted demo runs. If it is `0`, `false`, `no`, or `off`, the notebook calls the API. If the variable is unset, a missing `OPENAI_API_KEY` selects the demo and a present key selects the API. |
| `True` | Scripted demo, even when a key is set. No network call. |
| `False` | Chat Completions API. The run stops with a clear error if the key is empty. |

```bash
DEMO_MODE=1 jupyter nbconvert --to notebook --execute tutorial/1-using-tool.ipynb --output /tmp/1-using-tool-out.ipynb
```

`DEMO_MODE=0` is the live path. Temperature and max tokens come from `tutorial/common/client.py`.

In demo mode the tools, the loop, the checker, and the gates are the real functions. Only the model turn is scripted, so the printed trace is stable without an API key. A live model can phrase the answer differently. Demo checks raise when the scripted trace drifts. Live runs print a warning and continue.

The script does not print the API key.

## Shared pieces

| Path | Role |
|---|---|
| `runtime.py` | Loads the repository-root `.env` through `common/client.py` and exposes `chat`. |
| `demo_model.py` | Scripted tool-calling turns for `DEMO_MODE`. |
| `docs/` | `policy.md` and `faq.md`. The only shop documents `read_shop_file` may open. |
| `data/` | Notes, skills, the supplier page, the supplier note, and a fake canary. Not shop secrets. |
| `cell_src/` | Authoring copy of the cells. Notebooks inline this code so each file still runs alone. |
| `build_series.py` | Rewrites the notebooks from `cell_src/`. Companion notes are edited by hand. You do not need the script to study. |
| `common/client.py` | API key, model, temperature, max tokens. |
| `common/tools.py` | Path jail used by `read_shop_file`. |
| `common/autonomy.py` | Confirm tokens, and the never-tier for cards and outside mail. |

Runtime files under `tutorial/var/` (memory JSON and tickets) are gitignored.

## Rebuild

From the repo root, after editing `cell_src/`:

```bash
python tutorial/build_series.py
DEMO_MODE=1 python tutorial/build_series.py --check
```

`--check` executes every notebook's code cells in the scripted demo. It does not call the API.
