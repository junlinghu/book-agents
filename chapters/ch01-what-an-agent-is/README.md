# Ch 1. What an agent is

Part I — Foundations

This chapter fixes three words builders mix up — chatbot, workflow, and agent — and gives you one product equation to carry through the rest of the book: **Model × Harness × Feedback loop**. The running example is a desktop concierge for a fictional shop, Hearth Lane Café. By the end of the chapter you will have run a single chat completion with no tools, and you will have written down how it fails.

The lab is `labs/ch01-what-an-agent-is/`. Run instructions for the whole book are in the top-level README, under **Running the labs**.

## 1.1 Chatbot vs agent vs workflow

Three programs can all print a paragraph about a return. They are different programs.

**A chatbot** is a model call. You send messages. You get text back. The program ends. State is the transcript you choose to keep. A bad answer sits on the screen. The shop's files, inventory, and cash drawer are untouched, because the program never received a handle to them.

**A workflow** is control flow you wrote. A classifier, a template, a database query, and a final model call can all be steps, and the order of those steps is still yours. You can draw the branches before you see today's question. When the question is "what is the return window?", the workflow opens `policy.md`, then asks the model to answer from that text. The model does not choose the file. Your `if` does.

**An agent** is a model inside a loop that can choose the next action from a set you defined, see the result, and choose again, until a stop condition you also defined. The model proposes. Your code — the harness — performs the action and records the observation. For the same return question, the model may call `read_file` on `policy.md`, or on `faq.md`, or on both, or on a path that does not exist. You did not write that branch. You wrote the tool, the schema, and the rule that ends the loop.

The builder distinction is **who picks the next step**.

| | Who picks the next step | What the model is allowed to touch | Typical shape |
|---|---|---|---|
| Chatbot | Nobody. One call, then stop. | The messages you sent. | `messages → text` |
| Workflow | Your code. | Whatever the current step's function passes in. | `if / else` around model calls |
| Agent | The model, inside bounds. | The tools you registered, one call at a time. | `propose → execute → observe`, repeat |

Hearth Lane Café makes the difference concrete. A customer asks whether an opened bag of coffee can come back, and whether a cardamom bun can ship to another state.

- The Chapter 1 chatbot answers from weights and the system prompt. It has not opened a file. If it says "30 days, and yes we ship pastries," that number is not a shop rule. It is a prior.
- A workflow would be two lines you could write today: read `policy.md`, then one completion whose prompt contains that file. Correct, and boring, for this exact question. You already know which file matters.
- The agent shows up when you do not want to keep writing branches. "Is the bun safe for someone with a nut allergy, and is bike delivery open on Saturday for a $20 order?" might need `faq.md` and `policy.md`, in an order that depends on what the first file said. The loop is how you avoid a new `if` for every combination.

Chapter 2 builds that loop. This chapter runs the chatbot on purpose, so you can see the ungrounded answer before you add machinery.

## 1.2 Agent quality = Model × Harness × Feedback loop

Treat agent quality as a product of three factors you can change separately.

**Model** is the weights behind the completion: instruction following, whether a tool call arrives as a `tool_calls` object, context length, and how readily the model invents a specific number. You select it with `MODEL` in `.env`. You do not train it in this book.

**Harness** is everything you write around the model. The system prompt, the tool list, argument schemas, the code that actually reads a file, path checks, stop conditions, temperature, max tokens, and what you refuse to let the process do. Chapters 1–3 keep the harness small. Later chapters add memory, skills, permissions, and confirmations. Those are still harness.

**Feedback loop** is how a wrong answer becomes a change. Today the feedback loop is you: you read the reply, you write down the miss, you decide whether the next edit is a prompt, a tool, or a different model. Later the feedback loop is a checker, a fixture, a trace, a metric. The job is the same. Something other than the drafting model has to be able to say "this failed."

"Product" means a near-zero factor dominates. It is a design reminder, not a score you multiply in a spreadsheet.

- Model near zero: the endpoint returns prose and never a `tool_calls` object. The loop in Chapter 2 has nothing to execute. A better prompt cannot read the disk by itself.
- Harness near zero: this chapter. The model can be strong and still cannot open `policy.md`. It will answer anyway, because a chat completion is trained to answer.
- Feedback near zero: the paragraph sounds finished, you do not record the invented return window, and you "fix" whichever factor you happen to enjoy editing. You will not know if the edit mattered.

Same customer question, three different repairs:

| What you saw | Factor to move | What you change |
|---|---|---|
| The reply states a return window the program could not have looked up | Harness | Give the model a `read_file` tool and require a path citation (Chapter 2) |
| The tool exists, and this model never calls it | Model | Point `.env` at a model that emits tool calls (Chapter 3) |
| The tool ran, the file was right, and the reply still drops the citation | Feedback | Write the miss down now. A checker that rejects uncited claims comes later in the book |

Do not spend the week on a larger model while the program still has no way to see the shop. Do not spend it on a new tool while you are not looking at the answers.

## 1.3 When an agent is the wrong tool

An agent is the wrong tool when you can already name the steps, when a single draft is the whole task, or when a wrong action is expensive and you have no gate in front of it.

Use a **workflow** when you can write the branch before you see the input. "Print today's hours from `faq.md` on the door sign" is a file read. A model in a loop adds a way to skip the file. "Pack coffee orders under $40 with a $6 shipping line" is arithmetic plus the policy file. Code should own that.

Use **one completion** when the task is a draft and nothing is looked up or changed. "Rewrite the cardamom bun description so it fits on a tent card" is a chatbot-shaped job. Tools would be ceremony.

Use an **agent** when the next action depends on the last observation, and writing every branch in advance turns into a second, worse program. The concierge question that might need the policy, or the FAQ, or both, or a follow-up read after an error string, is that case. You still bound it: one tool, a docs directory, a step cap.

Leave the agent out when the action spends money, sends mail, or deletes a row, until the harness has a confirm step. This book adds autonomy tiers later. Chapters 1–3 do not. The labs only read files and print text. If a reply offers to refund the customer, that offer is fiction. The process has no refund function. Treat the offer as a failure mode, not as a feature you forgot to wire up.

A practical test before you add a loop:

1. Can you list the steps on paper in order? Write a workflow.
2. Is success "a paragraph exists," with no fact to check? Write one completion.
3. Does the next file, query, or handoff depend on what came back? A loop can earn its place.
4. Can you say what a wrong answer looks like in one sentence? If you cannot, you have no feedback loop, and you are not ready to automate the task.

"The domain is messy" is not, by itself, a reason. Sometimes the mess is a policy you have not written down. Write `policy.md` first. Then decide whether the reader of that file is a function or a model.

## 1.4 The café Concierge story (what you'll build by Ch 26)

The product in this book is a **Local Shop Concierge** for Hearth Lane Café, a fictional neighborhood shop at 12 Hearth Lane, North Mill. It runs on your machine. It is a desktop program with a model client, not a hosted chat product you deploy in these labs.

The shop rules you will ground answers in are deliberately specific, so a generic retail prior is obviously wrong:

- Opened coffee is final sale. Unopened bags, valve seal intact, come back within 14 days as Hearth card credit, not cash.
- Pastries and anything refrigerated are not shipped. Coffee under $40 ships in the US for $6.00.
- Local bike delivery is $4.50, free over $35, Tuesday–Friday only, within 3 miles.
- The café is closed Monday. Tuesday–Friday hours are 7:30–15:30.
- Cardamom buns contain wheat, butter, and almonds. There is no nut-free prep area.
- The Wi-Fi password is printed on the paper receipt. It is not in the FAQ, and the agent must not invent one.

Those sentences live in `labs/ch02-your-first-loop/docs/policy.md` and `docs/faq.md`. Chapter 1's program does not read them. That is the demonstration.

The capstone, Chapter 26, is the same concierge with the harness filled in. One recorded run is expected to:

- read shop files
- query inventory
- fetch a page and compare a price
- remember a constraint such as an allergy or a budget across a restart
- propose a cart that a separate checker can reject
- wait for a person to confirm before an order is written
- open a ticket when something is out of stock
- leave a trace and a metric for the finished task

You are not building that system this chapter. You are building the first measurement: a concierge persona, one completion, and a written list of what it got wrong. Every later chapter adds one harness or feedback piece and keeps the shop. When a new idea shows up — memory, skills, MCP, autonomy — the test is whether it changes what the concierge does on a café task, not whether the idea has a name.

## 1.5 How to read this book (labs, `.env`, failure-first)

Read the chapter, run the lab, write down what the model did, then decide which factor moved. The prose is not a substitute for the trace on your machine. Models differ. Your three failure modes are the data.

**Labs** sit under `labs/`, one directory per chapter. Chapter 1 is `labs/ch01-what-an-agent-is/hello_concierge.py`. The script is the answer code: a single `chat.completions.create` call, no `tools` argument. Shared setup (Python 3.10+, a virtualenv, `pip install -r requirements.txt`, `.env`) is in the top-level README under **Running the labs**.

**`.env`** at the repo root is the only provider switch:

- `BASE_URL` — where the OpenAI-compatible API lives
- `API_KEY` — bearer token; Ollama ignores the value and still requires a non-empty string (`ollama`)
- `MODEL` — the model name that server expects

The committed template is `.env.example`. Defaults are local Ollama (`http://localhost:11434/v1`, `ollama`, `llama3.2`). Groq and OpenRouter are the same three variables; Chapter 3 is the lab that changes them and nothing else. `.env` is gitignored. Do not put a real key in a chapter, a lab, or a commit.

**Failure-first** means the early labs are supposed to miss. Chapter 1's system prompt tells the model it is the concierge and asks it to be specific. It does not hand over documents, and it does not say "abstain if you are unsure." Abstention instructions are harness. You are watching what a bare completion does with a shop question before that harness exists. Chapter 2 adds the loop and the cite-or-say-you-don't-know instruction together. That is two changes, not a controlled experiment. Chapter 3 holds the harness still and swaps only the model, which is the controlled comparison.

Desktop-first means the file reads happen on the machine where you run Python. If `BASE_URL` points at Groq or OpenRouter, the prompt and any tool results still leave the machine as the HTTP request. Chapter 3 says that again where the client is introduced. Chapter 1 sends only the system prompt and the question.

A no-model check of the later harness (path jail, stop conditions) is available once dependencies are installed:

```bash
python -m unittest labs.common.test_harness
```

That test does not call Ollama or a hosted API. Chapter 1's script does.

## Lab

**Hello Concierge — one completion, no tools.**

1. Finish **Running the labs** in the top-level README (Python 3.10+, venv, `pip install -r requirements.txt`, `.env`).
2. From the repo root:

```bash
python labs/ch01-what-an-agent-is/hello_concierge.py
```

Optional: pass your own question as arguments. The default asks about returning an opened bag of coffee and shipping a cardamom bun.

3. Read the reply, then the note the script prints under "What to notice."
4. Write down **three failure modes you actually saw** in this run. Use the script's list as a checklist, not as a pre-filled answer. Record quotes. "It said 30 days" is data. "It hallucinated" is a label.

What you should be able to point at in the output:

- `TOOLS=none`, so you can see the harness really did not register a tool.
- `BASE_URL` and `MODEL`, so you know which weights produced the paragraph.
- A specific shop claim, or an explicit hedge. Both are worth recording. A hedge is the model refusing a guess. A specific return window is a guess the program could not have checked.

Details, the default question, and a second prompt to try are in `labs/ch01-what-an-agent-is/README.md`.

## Builder takeaway

Agents earn their keep when the environment is messy and actions matter. A single completion is the right tool for a draft. It is the wrong tool for a shop rule. The next chapter puts a loop around the model so the rule can be read before it is quoted.
