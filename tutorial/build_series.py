#!/usr/bin/env python3
"""Regenerate tutorial notebooks 2–15.

Tutorial 1 is maintained by hand. This script does not rewrite it.

Companion notes (``N-slug.md``) are lecture prose maintained by hand.
This script does not rewrite them.

Each notebook calls ``tutorial.common.colab.setup_colab`` and shows the
code that lesson introduces. Earlier helpers are imported from
``tutorial.common``. A rebuild does not paste earlier lessons back in.

From the repo root:

    python tutorial/build_series.py
    python tutorial/build_series.py --check
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent / "cell_src"
OUT = Path(__file__).resolve().parent

FRAGMENTS = [
    (1, "Shared helpers", "helpers.py",
     "Schema, message copying, and the check used by every later cell."),
    (1, "Tutorial 1 — one tool", "facts.py",
     "`get_shop_fact` opens the shop document. The model only sees the string you return."),
    (2, "Tutorial 2 — files and the shelf", "shelf.py",
     "`read_shop_file` uses the path jail in `tutorial/common/tools.py`. `query_inventory` reads the shelf seeded in this notebook. The SQL stays in the function."),
    (4, "Tutorial 4 — notes under a budget", "notes.py",
     "The prompt gets titles. `read_note` returns one short body. The picnic note is over the cap on purpose."),
    (5, "Tutorial 5 — durable memory", "memory.py",
     "Rows live in JSON. A new message list does not delete the file."),
    (6, "Tutorial 6 — skills", "skills.py",
     "A skill is a procedure. It is not the system prompt and it is not a second menu."),
    (7, "Tutorial 7 — the web as a sensor", "web.py",
     "One allow-listed page, labeled untrusted. No open-ended browser."),
    (8, "Tutorial 8 — a separate checker", "verify.py",
     "The proposer and the checker are different functions. A bad quantity fails here."),
    (9, "Tutorial 9 — graders", "evals.py",
     "A tiny grader over the answer and the tool log. Keep a failure in the set."),
    (10, "Tutorial 10 — autonomy gate", "gate.py",
     "Auto, confirm, and never. Cards and mail use `tutorial/common/autonomy.py`."),
    (11, "Tutorial 11 — injection boundary", "injection.py",
     "Proposals copied from the page still have to pass the path jail and the gate."),
    (12, "Tutorial 12 — two roles", "roles.py",
     "The stocker computes the gap. The checker rejects any other quantity. The note is only data."),
    (13, "Tutorial 13 — trace spans", "trace.py",
     "Each span names the user, the agent, and the tool. Secrets are not fields."),
    (14, "Tutorial 14 — cost, latency, and a cache", "cost.py",
     "Token totals and an illustrative cost. A second read of the same document can hit the cache."),
]

# The notebook that introduces a fragment shows that file.
# Later notebooks import it from tutorial.common instead of pasting it.
#
# one_line, purpose, learn, and maps are author notes for each lesson.
# The learner-facing prose is the companion markdown, edited by hand.
LESSONS = [
    {
        "n": 1,
        "slug": "1-using-tool",
        "title": "Tool calling",
        "one_line": "Define a tool, let the model request it, run it, and send the result back.",
        "purpose": (
            "Show the Chat Completions tool-calling round trip on one Hearth Lane question. "
            "The model does not open `policy.md`. Your function does. The model only sees the tool result, "
            "then writes the answer."
        ),
        "learn": [
            "The tool schema is a JSON object with a name, a description, and parameters.",
            "An assistant message can contain `tool_calls` instead of a final answer.",
            "You execute the call, append a `role: tool` message, and call the model again.",
            "A shop rule in the answer should come from that tool result.",
        ],
        "maps": [
            ("One completion, no tools, as the contrast", "`tutorial/1-using-tool.ipynb`"),
            ("Tool result goes back into the thread", "`tutorial/3-agent-loop.ipynb` (`run_agent`)"),
            ("Tools are how the agent touches the shop", "`tutorial/common/tools.py` and `tutorial/docs`"),
        ],
        "intro": """\
# 1. Tool calling

You are building the counter concierge for Hearth Lane Café. This notebook is the first piece: one tool, two model calls.

The model must not invent the return rule. It asks for `get_shop_fact`. This process reads `docs/policy.md` and returns the Returns section. The second model call writes the answer from that string.

Later notebooks keep this tool and add more. Run this file from top to bottom. The model calls need `OPENAI_API_KEY`.
""",
    },
    {
        "n": 2,
        "slug": "2-data-and-files",
        "title": "Shop data and files",
        "one_line": "Add a document tool and a SQLite shelf tool beside the first fact tool.",
        "purpose": (
            "Give the concierge two sensors: shop markdown under the tutorial path jail, "
            "and the SQLite shelf seeded in this folder. The model still only proposes calls. "
            "The notebook from tutorial 1 still runs, as a second question at the bottom."
        ),
        "learn": [
            "A file tool should refuse paths that leave the docs folder.",
            "A shelf tool can run SQL that the model never gets to write.",
            "One assistant turn may request more than one tool.",
            "Low stock means on_hand is at or below the reorder point. The gap to par is a separate number.",
        ],
        "maps": [
            ("`read_file` path jail", "`tutorial/common/tools.py` and `tutorial/docs`"),
            ("Shelf rows and low stock", "`tutorial/cell_src/shelf.py`"),
        ],
        "intro": """\
# 2. Shop data and files

Tutorial 1 returned one policy section. This notebook keeps that tool and adds two sensors the counter actually needs.

`read_shop_file` reads `policy.md` or `faq.md` from `tutorial/docs`. The path check is `tutorial.common.tools.read_file`. `query_inventory` reads the shelf seeded in this notebook from SQLite. The model passes a filter, not a SQL string.

The run asks which items are low and whether oat milk can ship. Both answers have to come from tools.
""",
    },
    {
        "n": 3,
        "slug": "3-agent-loop",
        "title": "The agent loop",
        "one_line": "Repeat perceive, reason, act, and observe until a final answer or a stop.",
        "purpose": (
            "Wrap the tutorial 1 exchange in a loop with a step cap and a repeated-call stop. "
            "The same low-stock question now takes more than one model call. "
            "Two extra runs show the harness stopping without writing a customer answer."
        ),
        "learn": [
            "Each model call is one step: look at the thread, maybe call tools, read the results.",
            "`max_steps` ends the loop. The harness does not invent the rest of the answer.",
            "The same tool call, with the same arguments, stops on the third try.",
            "A final answer is the turn where the model calls no tool.",
        ],
        "maps": [
            ("Perceive, reason, act, observe", "`tutorial/3-agent-loop.ipynb` (`run_agent`)"),
            ("Stop reasons", "`tutorial/3-agent-loop.ipynb` (`final`, `max_steps`, `repeated_call`)"),
        ],
        "intro": """\
# 3. The agent loop

Tutorials 1 and 2 ran one exchange by hand: model, tools, model. A real question can need several of those exchanges.

`run_agent` is that exchange inside a `for` loop. It stops when the model answers, when the step cap hits, or when the same call repeats. The shelf tool and the file tool from tutorial 2 are imported above. This notebook adds the loop.
""",
    },
    {
        "n": 4,
        "slug": "4-context-engineering",
        "title": "Context engineering",
        "one_line": "Put note titles in the prompt and load bodies only when the question needs them.",
        "purpose": (
            "Show context rot with three huddle notes. Pasting every body overflows a small turn budget. "
            "A catalog of titles fits. The agent reads the oat-milk note and the Thursday bun note, "
            "checks the shelf, and leaves the long picnic note on disk."
        ),
        "learn": [
            "A turn budget is a character cap for what you put in the prompt on purpose.",
            "A per-note cap refuses an oversized body even if the model asks for it.",
            "Selection is a tool call, not a bigger paste.",
            "The shelf tool still confirms a number that also appears in a note.",
        ],
        "maps": [
            ("Notes, caps, and a map instead of a paste", "`tutorial/cell_src/notes.py` and `tutorial/data/notes`"),
        ],
        "intro": """\
# 4. Context engineering

The loop from tutorial 3 will read whatever you stuff into the prompt. Stuffing is how a Tuesday huddle turns into context rot.

This notebook adds a note catalog. Titles go in the system prompt. Bodies come back through `read_note`. One note is over the cap so you can see the refusal. The picnic note is long and useless for a carton count. The run should not load it.

The shelf tool is imported, so the oat-milk count is checked against the database as well as the note.
""",
    },
    {
        "n": 5,
        "slug": "5-memory",
        "title": "Session and durable memory",
        "one_line": "Save a guest constraint to JSON and recall it from a fresh message list.",
        "purpose": (
            "Separate the chat transcript from durable memory. Turn 1 stores Priya's almond allergy. "
            "Turn 2 starts a new message list and finds the row in the JSON file. "
            "Shop policy stays in the docs. It is not copied into memory."
        ),
        "learn": [
            "Session memory is the message list. It dies when you start a new list.",
            "Durable memory is a file. `memory_set` appends. `memory_search` reads.",
            "A guest allergy is a constraint on that guest, not a shop belief.",
            "The earlier tools and the loop still run in this same notebook.",
        ],
        "maps": [
            ("JSON memory that survives the process", "`tutorial/cell_src/memory.py`"),
        ],
        "intro": """\
# 5. Session and durable memory

The message list is the session. Close it and the sentences are gone. A guest allergy has to outlive that.

This notebook adds `memory_set` and `memory_search`. They read and write `tutorial/var/memory.json`. Turn 1 saves a constraint. Turn 2 builds a new message list on purpose, then searches the file. The loop is imported.
""",
    },
    {
        "n": 6,
        "slug": "6-skills",
        "title": "Skills as procedures",
        "one_line": "Load a recommend procedure, then follow it with memory and the FAQ.",
        "purpose": (
            "Keep a procedure out of the system prompt until the question needs it. "
            "The recommend skill says to search memory and read the FAQ. "
            "Priya's allergy is already on disk from a previous shift. The FAQ, not the skill, lists the bun."
        ),
        "learn": [
            "A skill is a markdown procedure with a name. `load_skill` returns it.",
            "The skill must not become a second copy of the menu.",
            "Memory from tutorial 5 is an input to the procedure.",
            "If the FAQ lists no safe pastry, the answer says so and refuses a nut-free promise.",
        ],
        "maps": [
            ("Skills as portable procedures", "`tutorial/cell_src/skills.py` and `tutorial/data/skills`"),
        ],
        "intro": """\
# 6. Skills

A system prompt that contains every procedure gets long and stale. A skill is a procedure you load when the question matches.

`load_skill` reads `data/skills/recommend.md`. The run then searches Priya's memory and reads `faq.md`. The skill tells the agent those steps. It does not list a price. Prices and allergens stay in the FAQ. The loop, memory, and the FAQ tool are imported.
""",
    },
    {
        "n": 7,
        "slug": "7-web-browse",
        "title": "The web as an untrusted sensor",
        "one_line": "Fetch one supplier page, label it untrusted, and keep the shelf separate.",
        "purpose": (
            "Treat a web page as a sensor, not as a manager. The only URL is a local Mill and Birch fixture. "
            "The page names a wholesale price and also tries to give orders. "
            "The answer may quote the price as untrusted. It may not obey the orders."
        ),
        "learn": [
            "Allow-list the URL. Everything else is an error.",
            "Wrap the text so a person can see the boundary.",
            "Page instructions are data. They do not add tools.",
            "The shelf count still comes from SQLite, not from the page.",
        ],
        "maps": [
            ("Fetch a page, do not treat it as instructions", "`tutorial/cell_src/web.py` and `tutorial/data/pages`"),
        ],
        "intro": """\
# 7. The web as a sensor

A supplier page is not a shop policy. This notebook adds `fetch_page` for one URL, served from a local HTML file so the lesson does not depend on the public internet.

The result starts with `UNTRUSTED PAGE TEXT`. The run asks for the oat-milk case price and also reads the shelf. Quote the page as a claim. Do not let it change a Hearth Lane price or start a charge. Tutorial 11 hardens that boundary. The shelf tool and the loop are imported above.
""",
    },
    {
        "n": 8,
        "slug": "8-verification",
        "title": "A verification loop",
        "one_line": "Score a restock proposal with a checker that does not trust the proposer's quantity.",
        "purpose": (
            "Split proposing from checking. A proposal that orders 1000 cartons and ships dairy fails. "
            "A proposal whose quantity is par minus on_hand, that does not ship, and that cites the shelf, passes. "
            "The agent then calls the same checker as a tool."
        ),
        "learn": [
            "The checker recomputes the gap from the database.",
            "Dairy and bakery do not ship, even if the proposal says they do.",
            "A missing citation is a failure.",
            "The agent's accepted plan is the one the checker accepted, not the boldest number.",
        ],
        "maps": [
            ("A separate checker with hard findings", "`tutorial/cell_src/verify.py`"),
        ],
        "intro": """\
# 8. Verification

The loop can sound sure and still be wrong. A checker is a second function with the rules written in code.

`verify_proposal` loads the shelf row itself. Quantity must be the gap. Shipping dairy fails. An empty citation fails. The notebook runs a bad proposal and a good one before the model is involved, then lets the agent call the checker. The shelf and the loop are imported above.
""",
    },
    {
        "n": 9,
        "slug": "9-evals",
        "title": "Evals from a small failure set",
        "one_line": "Grade two tool-using answers and keep one canned failure in the set.",
        "purpose": (
            "Start an eval set from behaviors you already care about: opened-coffee returns, shipping milk, "
            "and a canned answer that invents a Wi-Fi password. The grader looks at the text and the tool log. "
            "The canned row is supposed to fail."
        ),
        "learn": [
            "A case names the question, the required tool, phrases that must appear, and phrases that must not.",
            "Passing means the tool ran and the text matches. It does not mean the model felt confident.",
            "Keep the failure. Deleting it makes the set look healthier than the product is.",
            "The same agent loop from earlier tutorials produces the two live cases.",
        ],
        "maps": [
            ("Graders over traces, including a failure you keep", "`tutorial/cell_src/evals.py`"),
        ],
        "intro": """\
# 9. Evals

You already know two answers the concierge must get right, and one answer it once got wrong. That is an eval set.

`grade_answer` checks phrases and whether a tool ran. The opened-coffee case uses `get_shop_fact`. The milk case uses `read_shop_file`. The Wi-Fi case is a canned bad answer. It does not call the model. It stays in the set because it fails. Those two tools and the loop are imported above.
""",
    },
    {
        "n": 10,
        "slug": "10-autonomy-policy",
        "title": "Autonomy policy",
        "one_line": "Let reads run, hold a ticket for confirmation, and never charge a card.",
        "purpose": (
            "Put a gate in front of side effects. Shelf reads are auto. `write_ticket` is confirm. "
            "`charge_card` is never, even with a token for that exact call. "
            "The first restock run prints a token and writes nothing. The second run passes the token and writes one file."
        ),
        "learn": [
            "The harness decides. The wording of the user message does not.",
            "A confirm token matches one tool name plus one argument object.",
            "A token never promotes a never-tier tool.",
            "This gate uses `tutorial/common/autonomy.py` for cards and email.",
        ],
        "maps": [
            ("auto / confirm / never", "`tutorial/common/autonomy.py` and `tutorial/cell_src/gate.py`"),
        ],
        "intro": """\
# 10. Autonomy policy

A tool call is a proposal until the harness agrees. Reads can run. A restock ticket waits. A card charge does not run.

`gate_call` returns allowed, confirm_required, or denied. Confirm uses `approval_token` from `tutorial.common.autonomy`, so a different quantity is a different token. The notebook writes an oat-milk ticket only on the second run, after you pass the token from the first run. `charge_card` stays denied. The shelf and the loop are imported above.
""",
    },
    {
        "n": 11,
        "slug": "11-prompt-injection",
        "title": "Prompt injection and untrusted data",
        "one_line": "Read a poisoned supplier page as data, and refuse the actions it demands.",
        "purpose": (
            "The Mill and Birch page asks the concierge to charge a card, read `.env`, and change the bun price. "
            "The model is asked to report the wholesale price and not to call those tools. "
            "A second cell runs the bad proposals through the path jail and the autonomy gate anyway, "
            "because the boundary has to hold when the model is wrong."
        ),
        "learn": [
            "Untrusted text can sit in the thread. It does not edit the tool list.",
            "The docs path jail blocks `..` and any file that is not policy or FAQ.",
            "A canary token in a local fixture must not appear in the tool output.",
            "Mail to the counter is confirm. Mail to any other domain is never.",
        ],
        "maps": [
            ("Untrusted page text and a canary", "`tutorial/data/pages` and `tutorial/data/canary.env`"),
            ("The gate from the previous tutorial", "`tutorial/common/autonomy.py`"),
        ],
        "intro": """\
# 11. Prompt injection

Tutorial 7 labeled the supplier page. This notebook checks that the label is a boundary, not a comment.

The page says to ignore instructions, charge a card, and read a secret. The agent may quote the `$3.10` claim. It may not do the rest. `show_injection_boundaries` then runs those proposals through `read_shop_file` and `gate_call` so the result does not depend on the model being polite. The canary file is fictional. It must not show up in the tool output.
""",
    },
    {
        "n": 12,
        "slug": "12-multi-agent",
        "title": "Constrained roles and a handoff",
        "one_line": "Let a stocker propose from the shelf and a checker reject a note that says 1000.",
        "purpose": (
            "Two roles pass a structured artifact. The supplier note says to order 1000 bags. "
            "The stocker sets quantity to par minus on_hand and stores the note as untrusted data. "
            "The checker rejects an artifact that copied 1000. The chat model can load inputs. It does not get the last word."
        ),
        "learn": [
            "A handoff is a dict with a role, the shelf numbers, and the untrusted note.",
            "The checker compares the artifact to the shelf row. It does not trust the note.",
            "A failed check stops the handoff. It does not become an order.",
            "The fetch tool, the gate, and the loop are still in this notebook.",
        ],
        "maps": [
            ("Roles, contracts, and an untrusted supplier note", "`tutorial/cell_src/roles.py` and `tutorial/data/supplier-note.txt`"),
        ],
        "intro": """\
# 12. Multi-agent handoff

Two roles are safer than one model that plays every part. Here the roles are ordinary functions with a contract.

The stocker reads a shelf row and returns quantity as the gap. The checker accepts that artifact or rejects it. A draft that copies `1000` from the supplier note fails. The agent loop loads the shelf and the note. It does not skip the checker. The shelf and the loop are imported above.
""",
    },
    {
        "n": 13,
        "slug": "13-observability",
        "title": "Traces and identity",
        "one_line": "Record a span per tool call with the user, the agent, and the tool named.",
        "purpose": (
            "Print a structured trace for the low-stock question. Every span names `counter-lead`, "
            "`shop-concierge`, and the tool that ran. The trace does not copy API keys or the supplier canary. "
            "You can explain the run from the spans without reading the model provider's private logs."
        ),
        "learn": [
            "Identity is a field: user, agent, and tool are different actors.",
            "A confirm or an error is a status, not a hidden branch.",
            "Do not put secrets, page bodies, or raw credentials on a span.",
            "The answer is still grounded in the shelf and the policy file.",
        ],
        "maps": [
            ("Spans you can replay without a collector", "`tutorial/cell_src/trace.py`"),
        ],
        "intro": """\
# 13. Observability

When a restock goes wrong, you need the trace, not a guess about which tool ran. This notebook records spans inside `run_agent`.

Each span has a trace id, a status, and three identities: the user (`counter-lead`), the agent (`shop-concierge`), and the tool. The low-stock question from tutorial 3 runs again so you can see the same work with a trace attached. The shelf tools and the loop are imported above. Nothing secret belongs in the JSON.
""",
    },
    {
        "n": 14,
        "slug": "14-cost-latency",
        "title": "Cost, latency, and a cache",
        "one_line": "Log tokens, an illustrative cost, and latency, and cache a repeated document read.",
        "purpose": (
            "Ask for café hours twice in one loop. The first `read_shop_file` misses the cache. The second hits it. "
            "The ledger sums prompt tokens, completion tokens, latency, and an illustrative USD figure. "
            "`route_task` records which model class you would have picked. This lab still uses one model id."
        ),
        "learn": [
            "Usage belongs on the trace next to the answer, including failed or partial runs.",
            "A cache key is the tool name plus its arguments. Do not cache a ticket write.",
            "Routing is a decision you can log before you call a second model.",
            "The rates in the notebook are illustrative. They are not an invoice.",
        ],
        "maps": [
            ("Honest totals, not a proxy that flatters the run", "`tutorial/cell_src/cost.py`"),
            ("Cost, latency, and a read cache", "`tutorial/14-cost-latency.ipynb`"),
        ],
        "intro": """\
# 14. Cost and latency

A loop that hides its token count will surprise you on the second week. This notebook logs tokens, latency, and an illustrative cost on every model call.

It also caches read-only tools. The hours question reads `faq.md` twice. The second read should say `cache: HIT`. That second call is also the repeat nudge from tutorial 3. The cache still serves the file. A third identical call would stop the loop.

`route_task` prints whether the question looks like a short lookup or a shop decision. Both routes name `gpt-4.1-mini` here. Swapping the id is a change to `MODEL` in `tutorial/common/client.py`. The trace from tutorial 13 is imported, so spans are still recorded.
""",
    },
    {
        "n": 15,
        "slug": "15-shop-manager",
        "title": "Shop manager capstone",
        "one_line": "Plan a Tuesday restock, check it, wait for confirmation, and file the tickets.",
        "purpose": (
            "Compose the earlier tutorials into one restock. The run loads the restock skill, reads low stock, "
            "policy, the oat-milk note, and shop memory, fetches the supplier page as untrusted text, "
            "verifies the house-blend and oat-milk gaps, and waits to write tickets. "
            "A second run passes the two approval tokens and writes the files. No card is charged."
        ),
        "learn": [
            "A capstone is the same tools and gates, in one workflow, not a new framework.",
            "Quantity is the shelf gap: 14 bags of HB-12 and 13 cartons of OM-32 on this seed.",
            "Confirmation is per call. Two tickets, two tokens.",
            "The supplier note still cannot set the quantity, and the page still cannot grant a charge.",
        ],
        "maps": [
            ("One recorded restock from plan to ticket", "`tutorial/15-shop-manager.ipynb`"),
            ("The pieces above", "`tutorial/1-using-tool.ipynb` through `tutorial/14-cost-latency.ipynb`"),
        ],
        "intro": """\
# 15. Shop manager

This is the concierge with the earlier pieces working together. A manager asks for the Tuesday restock.

The loop loads the restock skill, reads the shelf, the policy, the oat-milk note, and shop memory, and fetches the supplier page as untrusted text. It verifies HB-12 and OM-32. Quantity is the gap on the shelf seed in this notebook: 14 bags of house blend (par 18, on hand 4) and 13 cartons of oat milk (par 16, on hand 3). Tickets wait for two approval tokens. The confirmed run writes the files. The checker still rejects a 1000-bag note. The page still cannot charge a card.

The tools this restock uses are imported above. The run at the bottom is the workflow.
""",
    },
]


def read_src(name: str) -> str:
    return (SRC / name).read_text(encoding="utf-8").rstrip() + "\n"


def bootstrap(lesson: dict) -> str:
    return textwrap.dedent(
        f"""\
        import sys
        from pathlib import Path


        def find_root():
            \"\"\"Repo root, whether the kernel started here or in tutorial.\"\"\"
            here = Path.cwd().resolve()
            for candidate in [here, *here.parents]:
                marker = candidate / "tutorial" / "common" / "client.py"
                if marker.is_file():
                    return candidate
            raise RuntimeError(
                "Open this notebook inside the book-agents repository. "
                "The setup cell looks for tutorial/common/client.py."
            )


        ROOT = find_root()
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from tutorial.common.client import describe_runtime
        from tutorial.runtime import chat, require_key

        LESSON = {lesson["slug"]!r}
        LESSON_NUMBER = {lesson["n"]}
        require_key()
        print("tutorial:", LESSON)
        print(describe_runtime())
        """
    )




def colab_markdown(slug: str) -> str:
    """Badge plus a short label for the Colab setup cell."""
    url = (
        "https://colab.research.google.com/github/junlinghu/book-agents/blob/main/tutorial/"
        + slug
        + ".ipynb"
    )
    badge = (
        "[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]("
        + url
        + ")"
    )
    return (
        badge
        + "\n\n"
        + "## Colab setup\n\n"
        + "Run the next cell first on Google Colab. "
        + "It sparse-checkouts this public repo and installs packages only when the kernel is Colab. "
        + "Local Jupyter and VS Code skip that work.\n\n"
        + "An API key is required. Set `OPENAI_API_KEY` in Colab secrets "
        + "(the key icon, secret name `OPENAI_API_KEY`) or in an environment cell: "
        + '`os.environ["OPENAI_API_KEY"] = "sk-..."`. '
        + "Do that before the lesson setup cell. "
        + "Locally, put the same name in the repository-root `.env`. "
        + "A missing key stops the notebook. The key is not printed.\n\n"
        + "Edits you make in Colab stay in that session. They do not push to GitHub."
    )


# First code cell. A fresh Colab runtime cannot import tutorial.common until
# this cell checks the repo out. setup_colab() does the install, the secret,
# and a second checkout if the marker is still missing.
COLAB_SETUP_CODE = textwrap.dedent(
    """\
    # Colab setup. Run this cell before the other code cells.
    # A fresh Colab runtime cannot import tutorial.common yet, so this cell
    # sparse-checkouts the repo first. Local Jupyter and VS Code skip that.
    #
    # An API key is required. On Google Colab, set OPENAI_API_KEY in one of these ways:
    #   * Secrets (the key icon): a secret named OPENAI_API_KEY
    #   * an environment cell: os.environ["OPENAI_API_KEY"] = "sk-..."
    # Locally, put the key in the repository-root .env.
    # Do not commit a key. This cell does not print the value.
    # Edits you make in Colab stay in the session. They do not push to GitHub.

    import sys
    from pathlib import Path


    def _on_colab():
        try:
            import google.colab
        except ImportError:
            return False
        return Path("/content").is_dir() and google.colab is not None


    def _use(root):
        if not (Path(root) / "tutorial" / "common" / "colab.py").is_file():
            return False
        text = str(root)
        if text not in sys.path:
            sys.path.insert(0, text)
        return True


    ready = False
    if _on_colab():
        repo = Path("/content/book-agents")
        if not _use(repo):
            import shutil
            import subprocess

            if repo.exists() and not (repo / ".git").exists():
                raise RuntimeError(
                    str(repo) + " exists but is not a git checkout. "
                    "Move that folder aside and run this cell again."
                )
            if repo.exists():
                shutil.rmtree(repo)
            url = "https://github.com/junlinghu/book-agents.git"
            try:
                subprocess.check_call([
                    "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                    url, str(repo),
                ])
                subprocess.check_call([
                    "git", "-C", str(repo), "sparse-checkout", "set", "tutorial",
                ])
            except subprocess.CalledProcessError:
                if repo.exists():
                    shutil.rmtree(repo)
                subprocess.check_call(["git", "clone", "--depth", "1", url, str(repo)])
            if not _use(repo):
                raise RuntimeError(
                    "Colab setup could not find tutorial/common/colab.py after cloning."
                )
        ready = True
    else:
        here = Path.cwd().resolve()
        for candidate in [here, *here.parents]:
            if _use(candidate):
                ready = True
                break
        if not ready:
            print("Not Colab. Skipped clone and pip install.")

    if ready:
        from tutorial.common.colab import setup_colab

        setup_colab()
    """
)



def read_loop() -> str:
    return (OUT / "common" / "loop.py").read_text(encoding="utf-8").rstrip() + "\n"


def own_fragment(n: int):
    """The single cell_src file this lesson introduces, if it has one."""
    for minimum, title, filename, blurb in FRAGMENTS:
        if minimum == n:
            return title, filename, blurb
    return None


def standalone_note() -> str:
    return (
        "Shared helpers this lesson needs are imported, not copied from earlier notebooks. "
        "You can run this file by itself."
    )


SHARED_MD = (
    "## Shared pieces\n\n"
    "These imports are the earlier pieces this lesson uses. "
    "They come from `tutorial.common` and `tutorial.runtime`. "
    "You do not need to run the previous notebook first.\n"
)

# Code shown in the lesson that introduces the loop. Later lessons import run_agent.
LOOP_SECTION = (
    "Tutorial 3 — the agent loop",
    "One step is one model call. Tool results are the observation. "
    "The loop stops on a final answer, on `max_steps`, or on a repeated call. "
    "It does not write a customer answer when it stops early. "
    "Tutorials 10, 13, and 14 register a gate, spans, and a cache on `HOOKS`. "
    "Those stay off in this notebook.",
)

# Names the demo cell uses, plus imports whose only job is to register a tool.
IMPORTS = {
    2: textwrap.dedent(
        """\
        import json

        from tutorial.common.facts import get_shop_fact  # registers the tutorial 1 tool
        from tutorial.common.harness import (
            TOOLS,
            assistant_message,
            call_tool,
            check,
            preview,
            system_text,
        )
        from tutorial.runtime import chat
        """
    ),
    3: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.shelf import reset_db
        """
    ),
    4: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    5: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        """
    ),
    6: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.memory import memory_set, reset_memory
        from tutorial.common.shelf import read_shop_file  # registers the FAQ tool
        """
    ),
    7: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    8: textwrap.dedent(
        """\
        import json

        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    9: textwrap.dedent(
        """\
        from tutorial.common.facts import get_shop_fact  # registers the return-rule tool
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import read_shop_file, reset_db
        """
    ),
    10: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    11: textwrap.dedent(
        """\
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        from tutorial.common.web import fetch_page  # registers the page tool
        """
    ),
    12: textwrap.dedent(
        """\
        import json

        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db, row_for
        """
    ),
    13: textwrap.dedent(
        """\
        import json

        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    14: textwrap.dedent(
        """\
        import json

        import tutorial.common.trace  # installs span hooks on the loop
        from tutorial.common.harness import check, system_text
        from tutorial.common.loop import run_agent
        from tutorial.common.shelf import reset_db
        """
    ),
    15: textwrap.dedent(
        """\
        import json
        import re

        import tutorial.common.trace  # installs span hooks on the loop
        from tutorial.common.cost import cost_summary, reset_cache
        from tutorial.common.gate import TICKETS, reset_tickets
        from tutorial.common.harness import check, system_text
        from tutorial.common.injection import show_injection_boundaries
        from tutorial.common.loop import run_agent
        from tutorial.common.memory import memory_set, reset_memory
        from tutorial.common.notes import read_note
        from tutorial.common.roles import checker, read_supplier_note, stocker
        from tutorial.common.shelf import reset_db, row_for
        from tutorial.common.skills import load_skill
        from tutorial.common.verify import verify_proposal
        from tutorial.common.web import fetch_page
        """
    ),
}

# A later notebook must not redefine a piece an earlier lesson introduced.
INTRODUCED = {
    2: ["def query_inventory(", "def read_shop_file("],
    3: ["def run_agent("],
    4: ["def list_notes(", "def read_note("],
    5: ["def memory_set(", "def memory_search("],
    6: ["def load_skill("],
    7: ["def fetch_page("],
    8: ["def verify_proposal("],
    9: ["def grade_answer("],
    10: ["def gate_call(", "def write_ticket("],
    11: ["def show_injection_boundaries("],
    12: ["def stocker(", "def checker("],
    13: ["def make_span(", "def root_span("],
    14: ["def cached_call(", "def cost_summary("],
}


def notebook_for(lesson: dict):
    n = lesson["n"]
    if n == 1:
        raise RuntimeError("Tutorial 1 is maintained by hand and is not regenerated.")
    cells = [
        new_markdown_cell(colab_markdown(lesson["slug"])),
        new_code_cell(COLAB_SETUP_CODE),
        new_markdown_cell(textwrap.dedent(lesson["intro"]).strip() + "\n\n" + standalone_note()),
        new_markdown_cell(
            "## Setup\n\n"
            "This notebook calls the OpenAI Chat Completions API. `OPENAI_API_KEY` is required. "
            "Locally the key is loaded from the repository-root `.env` by `tutorial/common/client.py`. "
            "On Colab, the setup cell above reads a secret of the same name. "
            "The value is not printed. A missing key stops the run.\n\n"
            "Companion notes: `" + lesson["slug"] + ".md`."
        ),
        new_code_cell(bootstrap(lesson)),
        new_markdown_cell(SHARED_MD),
        new_code_cell(IMPORTS[n]),
    ]
    if n == 3:
        title, blurb = LOOP_SECTION
        cells.append(new_markdown_cell("## " + title + "\n\n" + blurb))
        cells.append(new_code_cell(read_loop()))
    else:
        fragment = own_fragment(n)
        if fragment:
            title, filename, blurb = fragment
            cells.append(new_markdown_cell("## " + title + "\n\n" + blurb))
            cells.append(new_code_cell(read_src(filename)))
    cells.append(new_markdown_cell(
        "## Run\n\n"
        "`system_text()` mentions only the tools imported above. "
        "Run this cell after the ones above. Each model turn calls the Chat Completions API. "
        "A check prints a warning when the wording differs from the expected trace, and the notebook continues."
    ))
    demo_name = "demo_" + f"{n:02d}" + ".py"
    cells.append(new_code_cell(read_src(demo_name)))
    notebook = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
    )
    return notebook


def write_series() -> None:
    """Rewrite notebooks 2–15. Leave tutorial 1 and the companion notes untouched."""
    for lesson in LESSONS:
        if lesson["n"] == 1:
            print("skip", lesson["slug"], "(kept as the short tool lesson)")
            continue
        path = OUT / (lesson["slug"] + ".ipynb")
        nbformat.write(notebook_for(lesson), path)
        print("wrote", path.relative_to(ROOT))


FORBIDDEN = (
    "DEMO_MODE",
    "USING_DEMO",
    "using_demo",
    "describe_mode",
    "demo_model",
    "scripted_turn",
    "scripted demo",
    "scripted model",
    "scripted lesson",
    "scripted demonstration",
    "scripted run",
)


def check_series() -> None:
    """Compile notebook code and fail if a demo flag remains. Does not call the API."""
    import os

    leftovers = []
    for path in sorted(OUT.rglob("*")):
        if path.suffix not in {".py", ".md", ".ipynb"}:
            continue
        # This file names the tokens it searches for.
        if path.name == "build_series.py":
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                leftovers.append(str(path.relative_to(ROOT)) + ": " + token)
    if leftovers:
        raise SystemExit("demo flags remain:\n" + "\n".join(leftovers))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    for lesson in LESSONS:
        path = OUT / (lesson["slug"] + ".ipynb")
        notebook = nbformat.read(path, as_version=4)
        print("compile", lesson["slug"])
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            try:
                compile(cell.source, f"{lesson['slug']}#{index}", "exec")
            except SyntaxError:
                print("FAILED cell", index, "in", lesson["slug"])
                raise
        code_cells = [cell.source for cell in notebook.cells if cell.cell_type == "code"]
        if code_cells[0].strip() != COLAB_SETUP_CODE.strip():
            raise SystemExit(lesson["slug"] + " Colab cell does not call tutorial.common.colab")
        if "def in_colab(" in code_cells[0]:
            raise SystemExit(lesson["slug"] + " still inlines the Colab setup")
        if lesson["n"] == 1:
            continue
        code = "\n".join(code_cells)
        prose = "\n".join(cell.source for cell in notebook.cells)
        if "copied forward" in prose:
            raise SystemExit(lesson["slug"] + " still says earlier lessons were copied forward")
        for earlier, markers in INTRODUCED.items():
            if earlier >= lesson["n"]:
                continue
            for marker in markers:
                if marker in code:
                    raise SystemExit(lesson["slug"] + " still defines " + marker)
        for marker in INTRODUCED.get(lesson["n"], []):
            if marker not in code:
                raise SystemExit(lesson["slug"] + " is missing " + marker)

    os.environ["OPENAI_API_KEY"] = ""
    from tutorial.runtime import chat, require_key

    for fn in (require_key, lambda: chat([{"role": "user", "content": "hi"}], [])):
        try:
            fn()
        except RuntimeError as error:
            if "OPENAI_API_KEY" not in str(error):
                raise
        else:
            raise SystemExit("a missing OPENAI_API_KEY did not raise")
    print("ok: notebooks compile, demo flags are gone, a missing key raises")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Local Shop Concierge tutorial notebooks.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild, compile every notebook code cell, and fail if a demo flag remains. Does not call the API.",
    )
    args = parser.parse_args(argv)
    write_series()
    if args.check:
        check_series()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
