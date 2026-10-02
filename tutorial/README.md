# Harbor Jar tutorial

Fifteen notebooks that build one seller for the fictional Harbor Jar, a small-batch shop of preserves, olive oils, spice blends, and gift boxes. The person in the chat is a customer on the store website. The agent is the seller: it answers support questions and walks a customer through a guarded purchase. Each lesson adds one idea. From tutorial 2 on, a notebook imports the earlier helpers it uses, so you can run any notebook by itself.

This folder carries its own OpenAI client (`common/client.py`), store policy and FAQ (`docs/`), path jail (`common/read_file.py`), catalog database (`common/get_db.py` and `common/read_db.py`), tool registry (`common/tools.py`), and autonomy gate (`common/autonomy.py` and `common/gate.py`). Nothing here imports a file outside `tutorial/`. Runtime helpers live in `common/`.

## Status

| # | Notebook | Summary | Status |
|---|---|---|---|
| 1 | [1-using-tool](1-using-tool.ipynb) | Define a tool, let the model request it, run it, and send the result back. Opened jar. | Ready |
| 2 | [2-tools-and-loop](2-tools-and-loop.ipynb) | Catalog in SQLite plus the perceive–reason–act–observe loop. Chili oil to Ohio. | Ready |
| 3 | [3-context-engineering](3-context-engineering.ipynb) | Help-article titles in the prompt; bodies loaded on purpose. Mega-guide refused. | Ready |
| 4 | [4-memory](4-memory.ipynb) | Session messages versus one shared customer preference file. Maya in a fresh session. | Ready |
| 5 | [5-skills](5-skills.ipynb) | A procedure file, separate from the system prompt and the tools. Recommend for Maya. | Ready |
| 6 | [6-web-browse](6-web-browse.ipynb) | One origin page, treated as an untrusted sensor. | Ready |
| 7 | [7-verification](7-verification.ipynb) | A checker that does not trust the proposed quantity, ship flag, or citation. | Ready |
| 8 | [8-evals](8-evals.ipynb) | A graded set of support and buy cases, including one canned failure. | Ready |
| 9 | [9-autonomy-policy](9-autonomy-policy.ipynb) | Auto, confirm, and never gates. | Ready |
| 10 | [10-prompt-injection](10-prompt-injection.ipynb) | Untrusted page text cannot grant tools or reveal a canary. | Ready |
| 11 | [11-multi-agent](11-multi-agent.ipynb) | An advisor and a fulfillment checker. Quantity comes from the catalog. | Ready |
| 12 | [12-observability](12-observability.ipynb) | Spans that name the customer, the agent, and the tool. | Ready |
| 13 | [13-cost-latency](13-cost-latency.ipynb) | Token, cost, and latency ledger, plus a read cache. | Ready |
| 14 | [14-planning](14-planning.ipynb) | An explicit plan, then the loop acts. | Ready |
| 15 | [15-guided-purchase](15-guided-purchase.ipynb) | One chat until the customer leaves: recommend, cart, verify, gate, and an order note. No silent charge. | Ready |

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

Each lesson has a companion note, `N-slug.md`, that places the lesson on the path from a single tool to a guided purchase and points at the matching helpers. How to run a notebook is in the sections above.

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
| `docs/` | `policy.md` and `faq.md`. `get_store_fact` maps a topic onto a section in these files. The model does not pass a path. |
| `data/` | Help articles, the shared customer preference file, skills, the origin page, the origin note, and a fake canary. Not store secrets. |
| `common/colab.py` | Shared Colab clone, package install, and secret copy. Notebooks point at `setup_colab` here. |
| `common/client.py` | API key, model, temperature, max tokens. |
| `common/tools.py` | Chat Completions registry: schemas, `register`, and `call_tool`. Leaf modules register tools here. The loop does not import those leaves. |
| `common/read_file.py` | Path jail and document reading. Not a Chat Completions tool. The topic lookup calls it with a path the program chose. |
| `common/get_db.py` | Catalog seed, `reset_db`, and the database connection. |
| `common/read_db.py` | Catalog reads: `row_for` and `catalog_rows`. The SQL stays here. |
| `common/autonomy.py` | Confirm tokens, and the never-tier for cards, cancellations, and customer email. |
| `common/harness.py` | Paths, `system_text`, and checks. Notebooks import this instead of copying earlier cells. |
| `common/loop.py` | `run_agent` starts a fresh list. `run_turn` continues a list the caller kept. A gate, spans, and a cache turn on when those lessons are imported. The plan turns on when tutorial 14 or tutorial 15 registers `draft_plan`. |
| `common/facts.py`, `catalog.py`, `articles.py`, `memory.py`, `skills.py`, `web.py`, `verify.py`, `evals.py`, `gate.py`, `injection.py`, `roles.py`, `trace.py`, `cost.py` | Lesson helpers. Later notebooks import these. |

Runtime files under `tutorial/var/` (order notes) are gitignored. Customer preferences live in `data/customer_preference.md`. Tutorial 14 defines `draft_plan` and `plan_steps` in `14-planning.ipynb`, not under `common/`. `draft_plan` is one model call with an empty tool list, registered on `HOOKS` before the loop acts. Tutorial 15 defines `run_customer_chat` in `15-guided-purchase.ipynb`, not under `common/`. That function is one visit until the customer says bye. A headless run replays demo lines. The visit registers the same plan hook so a standalone run still drafts one plan.

## Editing

Edit the notebooks and the modules in `common/` directly. Supporting functions live in `common/`. A notebook shows only that lesson's new step. Companion notes (`N-slug.md`) are edited by hand.
