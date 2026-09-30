# Lab — Chapter 9. Protocols and the open agent stack

Two teaching servers speak MCP method names over line-delimited JSON-RPC. The concierge may call them only that way. Contract tests check schemas and the register without calling a model.

Chapter: [Chapter 9: Protocols and the Open Agent Stack](../../chapters/ch09-protocols-and-open-stack/README.md)

## Goal

Finish `servers/sql_server.py` and `servers/fetch_server.py`. Finish `concierge.py` so a customer question about the bun price is answered from `tools/call` results. `concierge.py` must not open SQLite and must not call HTTP itself. A2A stays a survey. You do not build a second agent.

## Assignment

Turn in:

1. The output of `python labs/ch09-protocols-and-open-stack/test_contract.py` when it passes.
2. A captured `initialize` and `tools/list` exchange for each server, including the server version.
3. A concierge trace for the default question: which server handled which call, the tool results, and the answer. The bun's register cents and a quote from the board should both be visible in the tool results.
4. A note that says where the database driver and the HTTP client are imported. The answer this lab wants is the server files, not `concierge.py`.
5. Optional: one sentence on what an agent card would advertise if a restock agent drafted the order and this concierge only received the draft. Do not implement that agent.

## Prerequisites

- The shared setup in [`../README.md`](../README.md): Python 3.10 or newer and a virtualenv
- A model that can emit tool calls, for the concierge trace only. The contract tests do not need one

## Setup

Do the shared setup in [`../README.md`](../README.md) once, then come back here.

This lab does not install an MCP SDK. Servers read and write one JSON object per line on stdin and stdout. Method names to handle: `initialize`, `tools/list`, and `tools/call`. That is enough of the protocol for the café. You can ignore the rest of the specification.

## Files

| Path | Role |
|---|---|
| `rpc.py` | Read and write one JSON message per line. Use this from the servers and the host |
| `data/seed.sql`, `init_db.py` | Register. The cardamom bun is 475 cents |
| `servers/sql_server.py` | Stub. Version string is `shop-sql/0-todo` until you set `shop-sql/1` |
| `servers/fetch_server.py` | Stub. Allow only `http://127.0.0.1:8765/`. Version starts at `shop-fetch/0-todo` |
| `site/shop.html` | Board to serve on port 8765. Contains the same kind of bait as Chapter 8 |
| `concierge.py` | Stub host. `list_tools` and `call_tool` raise `NotImplementedError` |
| `test_contract.py` | Schema, price, write refusal, allowlist refusal, and a check that the concierge file does not import the drivers |

`tools/call` results should be text the model can read. A dict with a `content` list of `{"type": "text", "text": "..."}` works with the contract test. So does a dict with a `text` field. Errors begin with `ERROR:`.

The SQL tool accepts one read. Refuse writes and refuse more than one statement. Cap the rows. The fetch tool refuses any URL that does not start with the allowlisted prefix, and it does not send that request.

## Steps

From the repo root, with the virtualenv active.

1. Build the register.

   ```bash
   python labs/ch09-protocols-and-open-stack/init_db.py
   ```

2. Finish both `handle` functions. Set the version constants to `shop-sql/1` and `shop-fetch/1` when the tools match the tests.

3. Run the contract tests. They do not call the OpenAI API.

   ```bash
   python labs/ch09-protocols-and-open-stack/test_contract.py
   ```

4. Serve the board in another terminal.

   ```bash
   python -m http.server 8765 --directory labs/ch09-protocols-and-open-stack/site
   ```

5. Finish `concierge.py`. Start each server as a subprocess, speak JSON-RPC through `rpc.py`, and pass only those tool results into the model loop. Reuse the client in `labs/common/client.py`. Do not add `tool_choice`.

   A request the host sends looks like this. The model does not write this message. Your host does.

   ```json
   {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "sql_query", "arguments": {"sql": "SELECT price_cents FROM products WHERE sku = 'cardamom-bun'"}}}
   ```

6. Run the concierge.

   ```bash
   python labs/ch09-protocols-and-open-stack/concierge.py
   ```

   Print each server's version at startup. Print each `tools/call` name and the first line of the result.

## What to write up

Record:

- Contract-test summary (how many tests ran, and that they passed).
- Both version strings from `initialize`.
- Tool names returned by `tools/list`.
- The register result and the fetch result for the default question, plus the answer.
- Whether the answer followed the bait paragraph on the board.
- The file that imports the database driver, and the file that imports the HTTP client.

## Troubleshooting

- `NotImplementedError` from `tools/list` or `tools/call`: the handler is still the stub. The contract test will error there until you return a dict.
- Version assertion: `shop-sql/0-todo` or `shop-fetch/0-todo` means the constant is unchanged.
- `475` missing: the database was not seeded, the SELECT did not run, or the result text dropped the cents. The FAQ price is $4.75. The seed uses cents.
- Write statement returns rows: the server treated a mutation as a read. The test expects `ERROR:`.
- `example.com` returns page text: the allowlist did not run before the GET.
- Concierge test fails on `sqlite3` or `httpx`: that import is in `concierge.py`. Move the call behind the server.
- Empty model tool log, with servers that pass the contract tests: the host never offered the MCP tools, or the model skipped them. Those are different. Print `tools/list` before you change `MODEL`.
