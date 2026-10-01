# Local Shop Concierge tutorial

Fifteen notebooks that build one shop agent for the fictional Hearth Lane Café. The person in the chat is shop staff. The agent helps staff. Staff may ask on behalf of a guest, for example whether an opened bag of house coffee can be returned. Each lesson adds one idea from the book. From tutorial 2 on, a notebook imports the earlier helpers it uses, so you can run any notebook by itself.

This folder carries its own OpenAI client (`common/client.py`), shop policy and FAQ (`docs/`), path jail (`common/tools.py`), and autonomy gate (`common/autonomy.py`). The shelf rows are seeded in `common/shelf.py`. Nothing here imports a file outside `tutorial/`. Runtime helpers live in `common/`.

## Status

| # | Notebook | Summary | Status |
|---|---|---|---|
| 1 | [1-using-tool](1-using-tool.ipynb) | Define a tool, let the model request it, run it, and send the result back. | Ready |
| 2 | [2-data-and-files](2-data-and-files.ipynb) | The SQLite shelf, beside a topic lookup for the shipping rule. | Ready |
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

Every row in the table is ready. Run the notebooks in order, or open any one on its own. From tutorial 2 on, each notebook imports the earlier helpers it uses.

## Prerequisites

- Python 3.10 or newer
- A virtualenv and the repo requirements
- An OpenAI API key in `OPENAI_API_KEY`. Every model turn calls the Chat Completions API.

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

The notebooks do not embed a Colab setup code cell. The setup lives in `tutorial/common/colab.py`. On a fresh Colab runtime, clone this repository into the session first, then run `setup_colab` from that module before the lesson cells. The helper:

- Detects Colab (`google.colab` and a `/content` directory).
- Sparse-checkouts the public repository so `tutorial/` is on disk (`tutorial.common`, `docs/`, and the rest of the lesson). If the sparse checkout fails, it falls back to a shallow clone.
- Installs `openai`, `python-dotenv`, and `httpx` when those imports are missing.
- Sets the working directory and `sys.path` so `import tutorial` works.
- Copies a Colab secret named `OPENAI_API_KEY` when that variable is empty. The value is not printed.

Local Jupyter and VS Code can skip `setup_colab` when you already have the checkout. The helper itself skips the clone and the install when the kernel is not Colab.

Edits you make in Colab stay in the Colab session. They do not push to GitHub.

An API key is required on every run. On Colab, add a secret named `OPENAI_API_KEY` (the key icon), or set `os.environ["OPENAI_API_KEY"]` in a cell before the lesson setup cell. Locally, put the key in the repository-root `.env`. The notebooks do not print the key. A missing key stops the run with a clear error.

## The API

Every model turn uses the OpenAI Chat Completions API through `tutorial/common/client.py`. Temperature and max tokens live in that file.

```bash
jupyter nbconvert --to notebook --execute tutorial/1-using-tool.ipynb --output /tmp/1-using-tool-out.ipynb
```

That command calls the API. A live model can phrase an answer differently from one run to the next. Lesson checks print a warning when the wording differs, and the notebook continues.

The notebook does not print the API key.

## Shared pieces

| Path | Role |
|---|---|
| `runtime.py` | Loads the repository-root `.env` through `common/client.py` and exposes `chat`. Requires `OPENAI_API_KEY`. |
| `docs/` | `policy.md` and `faq.md`. `get_shop_fact` maps a topic onto a section in these files. The model does not pass a path. |
| `data/` | Notes, skills, the supplier page, the supplier note, and a fake canary. Not shop secrets. |
| `common/colab.py` | Shared Colab clone, package install, and secret copy. Notebooks point at `setup_colab` here. |
| `common/client.py` | API key, model, temperature, max tokens. |
| `common/tools.py` | Path jail used inside the topic lookup. Not a tool the model can call. |
| `common/autonomy.py` | Confirm tokens, and the never-tier for cards and outside mail. |
| `common/harness.py` | Tool list, `system_text`, and checks. Notebooks import this instead of copying earlier cells. |
| `common/loop.py` | `run_agent`. A gate, spans, and a cache turn on when those lessons are imported. |
| `common/facts.py`, `shelf.py`, `notes.py`, `memory.py`, `skills.py`, `web.py`, `verify.py`, `evals.py`, `gate.py`, `injection.py`, `roles.py`, `trace.py`, `cost.py` | Lesson helpers. Later notebooks import these. |

Runtime files under `tutorial/var/` (memory JSON and tickets) are gitignored.

## Editing

Edit the notebooks and the modules in `common/` directly. The notebook that introduces a helper shows that code in the notebook. Later notebooks import it from `common/`. Companion notes (`N-slug.md`) are edited by hand.
