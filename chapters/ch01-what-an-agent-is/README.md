# Chapter 1: What an Agent Is

Products that answer in natural language are spreading quickly, and the word *agent* is now applied to programs that do not work the same way. A chat window, a fixed pipeline, and a model that chooses its own next step can each return a paragraph about a shop policy. They do not share the same control, the same failures, or the same cost to operate. Whether you are building the system or deciding whether a team should build it, it helps to know which of the three you have.

This chapter defines those three programs—chatbot, workflow, and agent—and introduces the product equation carried through the rest of this book: **Model × Harness × Feedback loop**. A brief running example, a desktop concierge for a fictional neighborhood café, shows how the same question behaves under each design. The lab that follows runs the concierge as a single completion with no tools, so an ungrounded answer is visible before any further machinery is added.

## What Are Chatbots, Workflows, and Agents?

Three programs can each print a paragraph about a return. They are different programs. The distinction that matters is who picks the next step.

A **chatbot** is one model call. You send messages, and you receive text. The program then ends. Any state is the transcript you choose to keep. A poor answer remains on the screen. The shop’s files, inventory, and payments stay untouched, because the program was never given a way to reach them.

A **workflow** is control flow you wrote in advance. A classifier, a template, a database query, and a final model call may all be steps, and the order of those steps is still yours. You can draw the branches before today’s question arrives. When the question is what the return window is, the workflow opens `policy.md` and then asks the model to answer from that text. Your code chooses the file.

An **agent** is a model inside a loop. The model may choose the next action from a set you defined, see the result, and choose again, until a stop condition you also defined. The model proposes. Your code—the **harness**—performs the action and records the observation. For the same return question, the model may call `read_file` on `policy.md`, on `faq.md`, on both, or on a path that does not exist. You did not write that branch. You wrote the tool, its schema, and the rule that ends the loop.

| | Who picks the next step | What the model may touch | Typical shape |
|---|---|---|---|
| Chatbot | No one. One call, then stop. | The messages you sent. | `messages → text` |
| Workflow | Your code. | Whatever the current step passes in. | `if / else` around model calls |
| Agent | The model, inside bounds you set. | The tools you registered, one call at a time. | `propose → execute → observe`, and repeat |

The Local Shop Concierge, described later in this chapter, makes the difference concrete. Suppose a customer asks whether an opened bag of coffee can be returned, and whether a cardamom bun can be shipped to another state.

Under the Chapter 1 chatbot, the answer comes from the model’s weights and from the system prompt. No file has been opened. If the reply says “30 days, and yes, we ship pastries,” that number is a prior the model brought with it. It is a shop rule only if the shop’s own text says so, and this program has not seen that text.

A workflow for this exact question is short: read `policy.md`, then make one completion whose prompt contains that file. The result can be correct, because you already know which file matters.

An agent earns its place when you do not want a new branch for every combination of facts. A question about a nut allergy and about Saturday bike delivery for a $20 order may need `faq.md` and `policy.md`, in an order that depends on what the first file said. The loop is how you avoid writing an `if` for every pairing. Chapter 2 builds that loop. This chapter runs the chatbot on purpose, so you can see the ungrounded answer first.

## What Determines Agent Quality

Treat agent quality as a product of three factors you can change separately:

**Agent quality = Model × Harness × Feedback loop**

The **model** is the weights behind the completion. It determines how well instructions are followed, whether a tool call arrives as a `tool_calls` object, how long a context is accepted, and how readily a specific number is invented. In this book you select the model with `MODEL` in `.env`. You do not train it here.

The **harness** is everything you write around the model: the system prompt, the tool list, argument schemas, the code that actually reads a file, path checks, stop conditions, temperature, the token limit, and the actions the process must refuse. Chapters 1–3 keep the harness small. Later chapters add memory, skills, permissions, and confirmations. Those additions are still harness.

The **feedback loop** is the path from a wrong answer to a change. In these early chapters that path is you. You read the reply, write down the miss, and decide whether the next edit is a prompt, a tool, or a different model. Later, the feedback loop may be a checker, a fixture, a trace, or a metric. The job is the same. Something other than the drafting model has to be able to say that the answer failed.

The word *product* is a design reminder. A factor near zero dominates the result. It is a check you apply before you spend effort, and this book does not ask you to multiply the factors in a spreadsheet.

- A model near zero returns prose and never a `tool_calls` object. The loop in Chapter 2 then has nothing to execute. A clearer prompt cannot read the disk by itself.
- A harness near zero is this chapter. A strong model still cannot open `policy.md`. It will answer anyway, because a chat completion is trained to answer.
- Feedback near zero leaves a paragraph that sounds finished. The invented return window is never recorded, and the next edit lands on whichever factor is most convenient to change. You then have no way to tell whether the edit mattered.

The same customer question can call for three different repairs.

| What you observed | Factor to move | What you change |
|---|---|---|
| The reply states a return window the program could not have looked up | Harness | Give the model a `read_file` tool and require a path citation (Chapter 2) |
| The tool exists, and this model never calls it | Model | Point `.env` at a model that emits tool calls (Chapter 3) |
| The tool ran, the file was right, and the reply still drops the citation | Feedback | Record the miss now. A checker that rejects uncited claims comes later in this book |

For a product decision, move the factor that is actually near zero. A larger model does not repair a program that still cannot see the shop. A new tool does not repair a process in which no one is reading the answers.

## When an Agent Is the Wrong Tool

An agent is the wrong tool when you can already name the steps, when a single draft is the whole task, or when a wrong action is expensive and you have no gate in front of it.

Use a **workflow** when you can write the branch before you see the input. Printing today’s hours from `faq.md` on a door sign is a file read. A model in a loop adds a way to skip the file. Packing coffee orders under $40 with a $6 shipping line is arithmetic together with the policy file. Code should own that calculation.

Use **one completion** when the task is a draft and nothing is looked up or changed. Rewriting a cardamom-bun description so that it fits on a tent card is a chatbot-shaped job. Tools would add steps without a fact to check.

Use an **agent** when the next action depends on the last observation, and writing every branch in advance becomes a second, weaker program. The concierge question that might need the policy, the FAQ, both, or a follow-up read after an error string is that case. You still bound the loop: one tool, a documents directory, and a step cap.

Leave the agent out when the action spends money, sends mail, or deletes a row, until the harness includes a confirmation step. This book introduces autonomy tiers in a later chapter. Chapters 1–3 do not. The labs only read files and print text. If a reply offers to refund a customer, the process has no refund function. Treat the offer as a failure mode.

Before you add a loop, apply this test:

1. Can you list the steps on paper, in order? Write a workflow.
2. Is success “a paragraph exists,” with no fact to check? Write one completion.
3. Does the next file, query, or handoff depend on what came back? A loop may earn its place.
4. Can you say what a wrong answer looks like in one sentence? If you cannot, you have no feedback loop, and the task is not ready to automate.

A messy domain, by itself, is a weak reason to add an agent. Sometimes the mess is a policy you have not written down. Write `policy.md` first. Then decide whether the reader of that file should be a function or a model.

## A Running Example: The Local Shop Concierge

The product that runs through this book is a **Local Shop Concierge** for Hearth Lane Café, a fictional neighborhood shop at 12 Hearth Lane, North Mill. It runs on your machine. It is a desktop program with a model client. These labs do not deploy it as a hosted chat product.

The shop rules used to ground answers are deliberately specific, so a generic retail prior is easy to spot:

- Opened coffee is final sale. Unopened bags, with the valve seal intact, may be returned within 14 days as Hearth card credit, not cash.
- Pastries and anything refrigerated are not shipped. Coffee under $40 ships in the United States for $6.00.
- Local bike delivery is $4.50, free over $35, Tuesday through Friday only, and within 3 miles.
- The café is closed on Monday. Tuesday through Friday, the hours are 7:30–15:30.
- Cardamom buns contain wheat, butter, and almonds. There is no nut-free preparation area.
- The Wi-Fi password is printed on the paper receipt. It is absent from the FAQ, and the agent must not invent one.

Those sentences live in `labs/ch02-your-first-loop/docs/policy.md` and `docs/faq.md`. The program in this chapter does not read them. That omission is the demonstration.

The capstone in Chapter 26 is the same concierge with the harness filled in. One recorded run is expected to read shop files, query inventory, fetch a page and compare a price, remember a constraint such as an allergy or a budget across a restart, propose a cart that a separate checker can reject, wait for a person to confirm before an order is written, open a ticket when an item is out of stock, and leave a trace and a metric for the finished task.

You are not building that system in this chapter. You are taking the first measurement: a concierge persona, one completion, and a written list of what the model got wrong. Each later chapter adds one piece of harness or one piece of feedback and keeps the same shop. When a new idea appears—memory, a skill, a protocol, an autonomy tier—the test is whether it changes what the concierge does on a café task.

## How to Read This Book

Read the chapter, run the lab, write down what the model did, and then decide which factor moved. The prose is not a substitute for the trace on your machine. Models differ. The failure modes you observe are the data.

Labs live under `labs/`, with one directory per chapter. The script for this chapter, `labs/ch01-what-an-agent-is/hello_concierge.py`, is a single `chat.completions.create` call with no `tools` argument. Shared setup for the book—Python, a virtual environment, dependencies, and `.env`—is described in the repository README under **Running the labs**.

The file `.env`, at the repository root, is the only switch among providers.

| Variable | Role |
|---|---|
| `BASE_URL` | Where the OpenAI-compatible API lives |
| `API_KEY` | Bearer token. Ollama ignores the value and still requires a non-empty string (`ollama`) |
| `MODEL` | The model name that server expects |

The committed template is `.env.example`. The defaults are a local Ollama server: `http://localhost:11434/v1`, the key placeholder `ollama`, and the model `llama3.2`. Groq and OpenRouter use the same three variables. Chapter 3 is the chapter that changes them and leaves the harness in place. `.env` is gitignored. A real key does not belong in a chapter, a lab script, or a commit.

The early labs are designed to miss. The system prompt in this chapter tells the model that it is the concierge and asks it to be specific. It withholds the shop documents, and it gives no instruction to abstain when unsure. An abstention instruction is part of the harness. The exercise is to see what a bare completion does with a shop question before that harness exists. Chapter 2 adds the loop and a cite-or-say-you-do-not-know instruction together. Those are two changes, so the comparison with this chapter is not controlled. Chapter 3 holds the harness still and swaps only the model.

*Desktop-first* means file reads happen on the machine where you run Python. If `BASE_URL` points at Groq or OpenRouter, the prompt—and, in later chapters, any tool results—still leaves the machine inside the HTTP request. Chapter 3 returns to that point when the client is introduced. This chapter sends only the system prompt and the question.

Once dependencies are installed, the path restriction and the stop conditions of the later harness can be checked without calling a model. That check is described with the lab setup in the repository README. The script for this chapter does call the model.

## Lab

The exercise for this chapter is one completion and no tools. Run it, read the reply, and write down three failure modes that are actually present in that run. Quote the sentences. A stated return window is an observation. The word “hallucination,” used alone, is only a label for it.

The output should make three things visible: `TOOLS=none`, so you can see that no tool was registered; `BASE_URL` and `MODEL`, so you know which weights produced the paragraph; and either a specific shop claim or an explicit hedge. A hedge is the model declining to guess. A specific return window is a guess the program could not have checked.

Procedure, the default question, and a second prompt are in [`labs/ch01-what-an-agent-is/README.md`](../../labs/ch01-what-an-agent-is/README.md).

A single completion remains the right tool for a draft. It is the wrong tool for a shop rule. The next chapter places a loop around the model, so the rule can be read before it is quoted.
