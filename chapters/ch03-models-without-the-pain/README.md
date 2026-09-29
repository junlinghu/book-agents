# Ch 3. Models without the pain

Part I — Foundations

Chapter 2's loop calls "the model" as if that were one thing. It is an HTTP server that speaks a subset of the OpenAI chat-completions API. This chapter keeps the harness byte-for-byte and moves only three settings: `BASE_URL`, `API_KEY`, and `MODEL`. The lab is `labs/ch03-models-without-the-pain/swap_model.py`. It imports `run_file_agent` and reads the Chapter 2 docs. You switch Ollama, Groq, or OpenRouter by editing `.env` and running the script again.

The builder claim: **swap the model client; keep the harness stable.**

## 3.1 Hosted API vs local weights

Two places can run the weights.

**Local weights**, in these labs, mean [Ollama](https://ollama.com/download) on your machine. The process that serves `http://localhost:11434/v1` loads the model. There is no per-token invoice. A café policy sent as a prompt stays on that machine unless you have pointed Ollama itself at a remote host. You pay in RAM, disk, and latency. Small instruct models are the ones that fit this setup. They also drop tool calls more often.

**A hosted API**, here Groq or OpenRouter, means someone else's GPU. You send an API key. You pay in latency that is often lower and in money or a quota. The request body leaves your machine. That body includes the system prompt, the question, and — once the loop is running — the tool results. `read_file` still runs locally. The bytes it returns are then copied into the next completion request. "The file was read locally" and "the file was sent to the provider" are both true for a hosted run. Do not put secrets in `policy.md` and then point `BASE_URL` at a host you would not email that file to.

What does **not** change between the two:

- `labs/common/loop.py` (the loop, the stop conditions, the system prompt)
- `labs/common/tools.py` (the schema and the directory jail)
- `labs/ch02-your-first-loop/docs/` (the shop text)
- `TEMPERATURE` and `MAX_TOKENS` in `labs/common/client.py`

What does change is which weights see that harness, how reliably they fill `tool_calls`, and whether the prompt leaves the machine.

Use the local default while you are editing the loop. Use a hosted model when you need a cleaner tool-call trace to confirm the harness, or when you are doing the Chapter 3 comparison itself. The point of the comparison is the difference you can attribute to the model, because the harness did not move.

## 3.2 OpenAI-compatible clients (`base_url`, `model`, `api_key`)

The Python SDK is the `openai` package. Compatibility means you construct one client and keep the call shape stable:

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

That construction is `make_client` and the call inside `run_file_agent`. Three fields select the server:

| Variable | Role | Ollama default |
|---|---|---|
| `BASE_URL` | Origin of the HTTP API, including the `/v1` prefix the SDK appends routes to | `http://localhost:11434/v1` |
| `API_KEY` | Bearer token. Ollama requires a non-empty string and ignores the value. Hosted APIs check it. | `ollama` |
| `MODEL` | Model id the server expects. The id is not portable across vendors. | `llama3.2` |

`labs/common/client.py` loads those from the repo-root `.env` via `python-dotenv`, without overriding variables already set in the process. A missing `BASE_URL` or `MODEL` falls back to the Ollama defaults, so a forgotten file fails as a connection error you can read, not as a `KeyError`. A missing `API_KEY` becomes `ollama`. An **empty** `API_KEY` stays empty and `require_settings` exits. The harness will not replace a blank hosted key with the Ollama placeholder.

Every lab script prints `describe_runtime()` before the request:

```text
BASE_URL=http://localhost:11434/v1
MODEL=llama3.2
API_KEY=set (value hidden)
```

The key's value is not printed. If it ever appears inside an exception string, `redact` strips it. Copy `.env.example` to `.env`. Do not commit `.env`. The example file is the contract; the ignored file is the secret.

Provider blocks, commented, also live in `.env.example`. Uncomment one provider and comment the others. Two active `MODEL=` lines are a footgun: dotenv's last assignment wins, which is easy to misread.

| Provider | `BASE_URL` | `API_KEY` | Example `MODEL` |
|---|---|---|---|
| Ollama | `http://localhost:11434/v1` | `ollama` | `llama3.2` |
| Groq | `https://api.groq.com/openai/v1` | your Groq key | `llama-3.3-70b-versatile` |
| OpenRouter | `https://openrouter.ai/api/v1` | your OpenRouter key | `meta-llama/llama-3.3-70b-instruct` |

Model ids get retired. If the HTTP error says the model is unknown, the fix is a current id from that provider's model list, not a change to `loop.py`. Groq's tool-use docs are the list that matters for Groq: you need a model marked for **local** tool use (your process runs `read_file`). `llama-3.1-8b-instant` is the smaller Groq option in the same family. OpenRouter ids look like `vendor/name`. Confirm on the model page that tools are supported before you burn a run on a chat-only model.

`max_retries=0` is deliberate. A local server that is not running should fail once, in front of you. The SDK's default retry sleep makes a down Ollama look like a hang.

## 3.3 Picking a small open instruct model for labs

The labs need an **instruct** model: weights trained to follow a chat template (system, user, assistant, tool), not a base model that only continues text. A base model will not reliably emit `tool_calls`. Pulling one and pointing `MODEL` at it looks like a harness bug. It is a model-selection bug.

Constraints for the default:

- It fits a desktop (the Ollama `llama3.2` tag is a small instruct model).
- It is documented as tool-capable. Ollama can serve tools on its OpenAI-compatible `/v1/chat/completions` route, and `llama3.2` is the name this repo's `.env.example` uses.
- You can replace it without editing Python.

`llama3.2` will sometimes ignore the tool and answer in prose. That is useful data about the model factor. The Chapter 2 script prints a note when a final answer arrives with an empty tool log. Before you rewrite the loop, change only `MODEL`.

Fallbacks that keep the same client:

- Local: `ollama pull llama3.1`, then `MODEL=llama3.1`. Llama 3.1 is the model Ollama's own tool-calling write-up used first. It is larger than 3.2.
- Groq: `MODEL=llama-3.3-70b-versatile` or `MODEL=llama-3.1-8b-instant`, with `BASE_URL=https://api.groq.com/openai/v1`.
- OpenRouter: a current tool-capable id such as `meta-llama/llama-3.3-70b-instruct`, after you confirm the slug.

Pick the small local model for day-to-day loop edits. Pick the hosted model when you want a second trace of the same question. Chapter 3's lab question is chosen so a correct answer has to touch **both** files: the delivery fee is only in `policy.md`, and the closed day is only in `faq.md`. One model may read both and cite both. Another may answer "about five dollars, closed Sundays" and cite nothing. That pair of traces is the bake-off. You do not need a leaderboard. You need the stop tag, the tool log, and the two citations.

Sampling stays put during that bake-off. `TEMPERATURE` is `0.2` and `MAX_TOKENS` is `800`, both in `labs/common/client.py`. If you change them between the Ollama run and the Groq run, you no longer know which factor moved.

## 3.4 Temperature, max tokens, and tool-calling quirks by provider

**Temperature.** `0.2` keeps policy wording stable across reruns. A high temperature increases paraphrase and also increases malformed tool arguments. The café lab is a quoting task. Leave the constant low while you compare providers. Edit `TEMPERATURE` when you are studying the knob, and write down that you edited it.

**Max tokens.** 800 is enough for two short tool calls and a paragraph with paths. If `stopped` is `max_tokens`, or a tool result says the arguments were not valid JSON and the trace looks cut off, raise `MAX_TOKENS`. Do not "fix" a truncated tool call by switching vendors first. You would be changing two factors.

**`tool_choice` is not sent.** Ollama's OpenAI-compatible API supports `tools` and does not support `tool_choice`. Groq does support `tool_choice`. The shared client omits the field so one request shape runs on both. The cost is real: the harness cannot force `read_file`. A skip is a model behavior you observe, not a flag you flip in Chapter 3.

**`messages[].name` is not sent.** Groq's compatible API rejects that field with HTTP 400. Tool results in this loop carry `role`, `tool_call_id`, and `content` only. That is enough for Ollama and for Groq. If you add `name` to debug a trace, Groq runs break and Ollama runs do not, and you will misread the failure as a model problem.

**Arguments arrive as a string, except when they do not.** The loop parses a JSON string or a dict. Invalid JSON is an `ERROR:` observation, not a crashed process. That is the quirk you want the model to see, so the next turn can send `{"path": "policy.md"}`.

**Content shape.** Some servers return assistant content as a list of parts. `message_text` flattens string parts and `{type: text}` parts before the lab prints them. You should not grow a special case per vendor in this chapter. One normalizer is the harness. A new provider quirk belongs in a note in your lab log first, and in `labs/common/` only when the same code has to keep running.

**Groq compound models are the wrong tool for this lab.** Models such as `groq/compound` run Groq-hosted tools (web search, code execution) on Groq's side. They do not call the `read_file` function in your process. A run that "browses" instead of opening `policy.md` is that mismatch. Use a row in Groq's docs marked for local tool use.

**OpenRouter will happily route a model that cannot call tools.** The failure mode is an HTTP error, or a final prose answer with an empty trace, depending on the model. The script's provider note at the end of `swap_model.py` is there so the settings are next to the trace. The model page's tool flag is the thing to check before the run.

**Ollama must already be serving, and the tag must be pulled.** `BASE_URL` pointing at `localhost` does not start the daemon and does not download weights. `ollama pull llama3.2` and a running server are setup, documented in the top-level README. A connection error on Chapter 3 is that setup. It is not a defect in `swap_model.py`.

When a run misbehaves, change one line in `.env` or one constant in `client.py`, run the same script, and keep the previous trace. If you change the prompt, the tool, and the model in the same edit, you have lost the chapter.

## Lab

**Run the Chapter 2 agent on Ollama and on Groq (or OpenRouter) by editing `.env` only.**

Setup is **Running the labs** in the top-level README. From the repo root:

```bash
python labs/ch03-models-without-the-pain/swap_model.py
```

The default question is: "How much is local delivery, and which day are you closed?" A grounded answer cites `docs/policy.md` for $4.50 (free at $35, Tuesday–Friday, within 3 miles) and `docs/faq.md` for closed Monday.

Do this twice:

1. With the Ollama block in `.env` (`BASE_URL=http://localhost:11434/v1`, `API_KEY=ollama`, `MODEL=llama3.2`). If the tool log is empty, set `MODEL=llama3.1` only after `ollama pull llama3.1`, and say so in your notes.
2. With either the Groq block or the OpenRouter block from `.env.example`. Comment the Ollama lines so only one `BASE_URL` and one `MODEL` are active. Run the same command. Do not edit `swap_model.py`.

For each run, keep:

- the printed `BASE_URL` and `MODEL`
- the tool log (paths requested, `PATH:` or `ERROR:`)
- the stop tag and step count
- whether $4.50 and Monday each have a real citation

The script prints a provider cheat sheet after the answer (and after a connection error) so the three `.env` shapes stay next to the output. The lab README at `labs/ch03-models-without-the-pain/README.md` repeats the switch steps. Sampling constants are printed too (`TEMPERATURE`, `MAX_TOKENS`). If those numbers differ between your two runs, you edited the harness, and the comparison is no longer the one this chapter asks for.

## Builder takeaway

Swap the model client; keep the harness stable. `BASE_URL`, `API_KEY`, and `MODEL` select weights. The loop, the jail, the stop conditions, and the sampling constants are the product you are building. A provider quirk that forces a fork in `loop.py` is a harness bug worth fixing once, in the shared client — not a reason to keep a second agent per vendor.
