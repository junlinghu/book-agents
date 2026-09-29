# Chapter 3: Local and Hosted Models

Chapter 2 spoke of “the model” as if the name picked out a single object. In these labs the model is an HTTP server that speaks a subset of the OpenAI chat-completions API. This chapter keeps the harness unchanged and moves only three settings: `BASE_URL`, `API_KEY`, and `MODEL`. The lab script, `labs/ch03-models-without-the-pain/swap_model.py`, imports `run_file_agent` and reads the Chapter 2 documents. You switch among Ollama, Groq, and OpenRouter by editing `.env` and running that script again.

The practical claim is this: **swap the model client, and keep the harness stable.** For a product decision, that split is what makes a comparison interpretable. If the prompt, the tools, and the sampling constants move at the same time as the weights, you cannot say which factor changed the result.

## Where the Weights Run

The weights can run in two places.

**Local weights**, in these labs, mean [Ollama](https://ollama.com/download) on your machine. The process that serves `http://localhost:11434/v1` loads the model. There is no per-token invoice. A café policy sent as a prompt stays on that machine, unless you have pointed Ollama itself at a remote host. You pay in memory, disk, and latency. The models that fit this setup are small instruct models. They also drop tool calls more often.

A **hosted API**, here Groq or OpenRouter, means someone else’s GPU. You send an API key. You pay in money or in a quota, and the latency is often lower than a small model on a laptop. The request body leaves your machine. That body includes the system prompt, the question, and—once the loop is running—the tool results. `read_file` still executes locally. The bytes it returns are then copied into the next completion request. For a hosted run, both of the following are true: the file was read on your machine, and the file was sent to the provider. Do not place secrets in `policy.md` and then point `BASE_URL` at a host you would not send that file to.

What stays fixed between the two:

- `labs/common/loop.py` — the loop, the stop conditions, and the system prompt
- `labs/common/tools.py` — the schema and the directory limit
- `labs/ch02-your-first-loop/docs/` — the shop text
- `TEMPERATURE` and `MAX_TOKENS` in `labs/common/client.py`

What changes is which weights see that harness, how reliably they fill `tool_calls`, and whether the prompt leaves the machine.

Use the local default while you are editing the loop. Use a hosted model when you need a cleaner tool-call trace in order to confirm the harness, or when you are making the comparison this chapter asks for. The point of the comparison is a difference you can attribute to the model, because the harness did not move.

## How an OpenAI-Compatible Client Selects a Model

The Python package is `openai`. Compatibility means you construct one client and keep the shape of the call stable:

```python
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
    timeout=120.0,
    max_retries=0,
)
client.chat.completions.create(
    model=model,
    messages=messages,
    tools=[READ_FILE_TOOL],
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)
```

That construction is `make_client`, together with the call inside `run_file_agent`. Three fields select the server.

| Variable | Role | Ollama default |
|---|---|---|
| `BASE_URL` | Origin of the HTTP API, including the `/v1` prefix the SDK appends routes to | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama requires a non-empty string and ignores the value. Hosted APIs check it. | `ollama` |
| `MODEL` | Model identifier the server expects. The identifier is not portable across vendors. | `llama3.2` |

`labs/common/client.py` loads those values from the repository-root `.env` through `python-dotenv`, and it does not override variables already set in the process. A missing `BASE_URL` or `MODEL` falls back to the Ollama defaults. A forgotten file then fails as a connection error you can read. A missing `API_KEY` becomes `ollama`. An empty `API_KEY` stays empty, and `require_settings` exits. The harness will not replace a blank hosted key with the Ollama placeholder.

Every lab script prints `describe_runtime()` before the request:

```text
BASE_URL=http://localhost:11434/v1
MODEL=llama3.2
API_KEY=set (value hidden)
```

The key’s value is not printed. If it appears inside an exception string, `redact` removes it. Copy `.env.example` to `.env`. Do not commit `.env`. The example file is the contract. The ignored file is the secret.

Commented provider blocks also live in `.env.example`. Uncomment one provider and comment the others. Two active `MODEL=` lines are easy to misread: the loader’s later assignment is the one that takes effect.

| Provider | `BASE_URL` | `API_KEY` | Example `MODEL` |
|---|---|---|---|
| Ollama | `http://localhost:11434/v1` | `ollama` | `llama3.2` |
| Groq | `https://api.groq.com/openai/v1` | your Groq key | `llama-3.3-70b-versatile` |
| OpenRouter | `https://openrouter.ai/api/v1` | your OpenRouter key | `meta-llama/llama-3.3-70b-instruct` |

Providers retire model identifiers. If the HTTP error says the model is unknown, replace it with a current identifier from that provider’s model list, and leave `loop.py` unchanged. For Groq, the relevant list is the tool-use documentation: you need a model marked for **local** tool use, because your process runs `read_file`. `llama-3.1-8b-instant` is the smaller Groq option in the same family. OpenRouter identifiers look like `vendor/name`. Confirm on the model page that tools are supported before you spend a run on a chat-only model.

`max_retries=0` is deliberate. A local server that is not running should fail on the first attempt. The SDK’s default retry sleep makes a stopped Ollama process look like a hang.

## How to Choose a Small Instruct Model

The labs need an **instruct** model: weights trained to follow a chat template of system, user, assistant, and tool roles. A base model only continues text. It will not reliably emit `tool_calls`. Pulling one and pointing `MODEL` at it looks like a defect in the harness. It is a defect in model selection.

The default is constrained in three ways:

- It fits a desktop. The Ollama tag `llama3.2` is a small instruct model.
- It is documented as able to call tools. Ollama can serve tools on its OpenAI-compatible `/v1/chat/completions` route, and `llama3.2` is the name this repository’s `.env.example` uses.
- You can replace it without editing Python.

`llama3.2` will sometimes ignore the tool and answer in prose. That behavior is useful evidence about the model factor. The Chapter 2 script prints a note when a final answer arrives with an empty tool log. Before you rewrite the loop, change only `MODEL`.

Fallbacks that keep the same client:

- Local: pull `llama3.1`, then set `MODEL=llama3.1`. Llama 3.1 is the model Ollama’s own tool-calling notes used first. It is larger than 3.2.
- Groq: `MODEL=llama-3.3-70b-versatile` or `MODEL=llama-3.1-8b-instant`, with `BASE_URL=https://api.groq.com/openai/v1`.
- OpenRouter: a current tool-capable identifier such as `meta-llama/llama-3.3-70b-instruct`, after you confirm the slug.

Use the small local model for day-to-day edits to the loop. Use a hosted model when you want a second trace of the same question. The question in this chapter’s lab is chosen so that a correct answer has to touch both files. The delivery fee appears only in `policy.md`. The closed day appears only in `faq.md`. One model may read both and cite both. Another may answer with a round number and a wrong closed day, and cite nothing. That pair of traces is the comparison. You do not need a public leaderboard. You need the stop tag, the tool log, and the two citations.

Hold sampling fixed during that comparison. `TEMPERATURE` is `0.2` and `MAX_TOKENS` is `800`, both in `labs/common/client.py`. If you change them between the Ollama run and the Groq run, you no longer know which factor moved.

## How Sampling and Providers Differ

**Temperature.** A value of `0.2` keeps policy wording stable across reruns. A high temperature increases paraphrase, and it also increases malformed tool arguments. The café lab is a quoting task. Leave the constant low while you compare providers. Edit `TEMPERATURE` when you are studying that constant, and write down that you edited it.

**Maximum tokens.** Eight hundred tokens are enough for two short tool calls and a paragraph that includes paths. If `stopped` is `max_tokens`, or if a tool result says the arguments were not valid JSON and the trace looks cut off, raise `MAX_TOKENS`. Switching vendors first would change two factors at once.

**`tool_choice` is omitted.** Ollama’s OpenAI-compatible API accepts `tools` and does not accept `tool_choice`. Groq does accept `tool_choice`. The shared client omits the field so that one request shape runs on both. The cost is real: the harness cannot force `read_file`. A skipped call is model behavior you observe in the trace.

**`messages[].name` is omitted.** Groq’s compatible API rejects that field with HTTP 400. Tool results in this loop carry `role`, `tool_call_id`, and `content` only. That set is enough for Ollama and for Groq. If you add `name` while debugging a trace, Groq runs fail and Ollama runs do not, and the failure is easy to misread as a property of the model.

**Arguments.** Providers usually send `function.arguments` as a JSON string. Some local stacks send a dictionary. The loop accepts either form. Invalid JSON is an `ERROR:` observation, and the process continues. The model sees that error on the next turn and can send `{"path": "policy.md"}`.

**Content shape.** Some servers return assistant content as a list of parts. `message_text` flattens string parts and parts of the form `{type: text}` before the lab prints them. This chapter does not grow a special case for each vendor. One normalizer belongs in the harness. A new provider quirk belongs first in your lab notes, and in `labs/common/` only when the same code must keep running.

**Groq compound models are the wrong fit for this lab.** Models such as `groq/compound` run Groq-hosted tools, including web search and code execution, on Groq’s side. They do not call the `read_file` function in your process. A run that browses the web instead of opening `policy.md` is that mismatch. Use a model marked, in Groq’s documentation, for local tool use.

**OpenRouter can route a model that cannot call tools.** The failure is either an HTTP error or a final prose answer with an empty trace, depending on the model. The provider note at the end of `swap_model.py` keeps the settings next to the trace. The tool flag on the model page is what to check before the run.

**Ollama must already be serving, and the tag must already be pulled.** A `BASE_URL` that points at `localhost` does not start the daemon and does not download weights. Pulling `llama3.2` and running the server are setup steps, documented in the repository README. A connection error in this chapter is that setup. It is not a defect in `swap_model.py`.

When a run misbehaves, change one line in `.env` or one constant in `client.py`, run the same script, and keep the previous trace. If you change the prompt, the tool, and the model in the same edit, you can no longer tell which change produced the new trace.

## Lab

Run the Chapter 2 agent twice, once on Ollama and once on Groq or OpenRouter, changing only `.env` between the runs. The default question asks how much local delivery costs and which day the café is closed. A grounded answer cites `docs/policy.md` for $4.50 (free at $35, Tuesday through Friday, within 3 miles) and `docs/faq.md` for Monday.

For each run, keep the printed `BASE_URL` and `MODEL`, the tool log (paths requested, and `PATH:` or `ERROR:`), the stop tag and the step count, and whether $4.50 and Monday each have a citation you can verify in the file. The script prints a short provider note after the answer, and after a connection error, so the three `.env` shapes stay next to the output. It also prints `TEMPERATURE` and `MAX_TOKENS`. If those numbers differ between your two runs, you edited the harness, and the comparison is no longer the one this chapter asks for.

The switch steps are in [`labs/ch03-models-without-the-pain/README.md`](../../labs/ch03-models-without-the-pain/README.md).

Swap the model client, and keep the harness stable. `BASE_URL`, `API_KEY`, and `MODEL` select weights. The loop, the directory limit, the stop conditions, and the sampling constants are the product you are building. A provider quirk that forces a fork in `loop.py` is a harness defect worth repairing once, in the shared client. It is a weak reason to keep a second agent for each vendor.
