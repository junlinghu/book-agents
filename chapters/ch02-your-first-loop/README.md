# Chapter 2: The Agent Loop

An agent is a language model wrapped in a harness. The harness is the program that calls the model, offers the model tools, carries out the tool calls the model proposes, and returns each result as an observation the model can read. The claim of this chapter is that this loop is what makes the system an agent. A prompt can tell the model to speak as the concierge of Hearth Lane Café. A prompt cannot open the café’s policy, refuse a path that leaves the shop’s folder, or decide that the work is finished. The program around the model does those things. Without the loop, the model is a chatbot again: it can answer only from the messages it was given, and those messages do not contain the shop’s files.

This chapter builds that program once, with a single tool, and walks through it slowly. You will see the message list the model actually receives, the request the model is allowed to make, the moment your code opens a file, and the four reasons the loop is allowed to stop. The running example is still the café. A customer asks whether an opened bag of coffee can be returned, and whether a cardamom bun can be shipped to another state. Chapter 1 let the model answer that question from memory. This chapter requires the answer to come from a file the program has read.

## What the model can do by itself

A large language model, in the sense this book uses, is a system that reads a list of messages and writes the next message. You send the list to a server that holds the model’s weights, and the server returns a reply. That exchange is the whole of what the model does here. It has no folder of shop documents, no permission to touch the disk on your machine, and no way to send email, issue a refund, or look up a second fact after it has finished speaking.

The list of messages is therefore the model’s entire world on a given turn. In Chapter 1 that list held two messages. The first was a system prompt, which is the brief that tells the model what role to play. The second was the customer’s question. The shop’s rules were not in either message. When the model then named a return window, the number came from patterns in its training. Hearth Lane’s policy had never been placed in the messages, so the paragraph could sound finished while the program had never consulted the shop.

It helps to keep that limit in view, because the rest of the chapter is a way of respecting it. If a fact is going to appear in an answer as a shop rule, something in your program has to place the text of that rule into the message list before the model writes the answer. The model will not go and fetch the text on its own.

## The harness, and why a prompt is not an agent

The harness is the ordinary software you write around the model. Current descriptions of agent systems, including the Microsoft Agent Framework and the broader writing on agent harnesses, use that word for the same surrounding program. In one pass, the harness calls the model, offers a list of tools, runs a tool call when the model proposes one, appends the result to the messages, and calls the model again. It also enforces the limits that keep the process from running without end.

A tool call is a request the model writes. The action happens later, and only if your program chooses to carry the request out. In these labs the request names a function and supplies arguments. The arguments usually arrive as JSON, which is a small text format for labeled values. A request to read the policy names the function `read_file` and supplies one label, `path`, with the value `policy.md`. The model is allowed to write that request. Your program is the part that decides whether to honor it, opens the file if the path is allowed, and tells the model what came back.

Hold onto the division of work. The model proposes a tool call. The harness executes that call and reports what happened, by placing the file’s text, or an error string, back into the conversation. The model does not itself open the file. Your program opens it, and then your program tells the model the result. When you describe a run, keep those two sentences separate, because a careful prompt and a filesystem are different objects. Only the program can read the disk.

Researchers described one influential form of this arrangement as ReAct, a name formed from reasoning and acting. The pattern is that the model should not have to answer from memory in a single breath. It may consider what it needs, propose an action, read the result of that action, and only then decide whether it is ready to answer. The lab in this chapter is a small and strict version of that pattern. The only action on offer is `read_file`. The only files it may touch sit in one directory, `labs/ch02-your-first-loop/docs/`.

This is also why a prompt, however careful, is not an agent. The system prompt used by the lab names `policy.md` and `faq.md`. It tells the model to read a file before stating a rule, a price, an hour, or a fee. It tells the model to cite the path, or to say that the documents do not contain the answer. Those sentences are a brief for the loop. They shape what a cooperative model is likely to request, and they leave the file closed. If you keep the brief and remove the function that runs the loop, the program is a single completion again. The brief may ask for a citation. Nothing in the program has produced a file for the model to cite.

## The loop, one turn at a time

The core of the harness is a loop, and you can read it as ordinary control flow. While the task is not finished, the harness calls the model and passes the messages so far, together with the tool list. The model may reply in either of two ways. It may return ordinary text, which means it is ready to answer the customer. Or it may return one or more tool calls. If the reply contains tool calls, the harness executes each one, appends the result to the message list, and goes around again. If the reply contains no tool call, or if a stop rule fires, the harness ends the loop and records why it stopped.

```mermaid
flowchart TD
  start[Message list so far]
  call[Harness calls the model]
  choice{Model requested a tool}
  act[Harness runs the tool]
  observe[Harness appends the result]
  done[Harness returns the text]
  start --> call
  call --> choice
  choice -->|yes| act
  act --> observe
  observe --> call
  choice -->|no| done
```

*Figure 2.1. The core loop. The model proposes a tool call or a final answer. The harness executes a tool call, appends the result, and calls the model again.*

Figure 2.1 is the shape of a turn that is still allowed to continue. A stop rule can also end the loop during a tool call, or when the step budget runs out. Those cases are Figure 2.2, after the contract the tool has to meet.

The function that does this work is `run_file_agent`, in `labs/common/loop.py`. Each pass makes one completion of the following shape. The same tool list is offered every time.

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=[READ_FILE_TOOL],
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)
```

The call does not include a `tool_choice` field that would force the model to use `read_file`. Chapter 3 explains the practical reason: Ollama, the local server these labs use by default, does not accept that field on its compatible endpoint, so the shared client omits it for every provider. The consequence belongs in this chapter as well. The model is allowed to skip the tool and answer at once. When that happens, the lab prints a final answer and an empty trace. The loop ran, and the model chose not to use the tool. Treat that paragraph as ungrounded until the trace shows a read, just as you treated the reply in Chapter 1.

Let us walk the café question through a cooperative run, and keep track of what the model can see at each step. The customer writes: "I opened a bag of your house coffee and they’re not for me. Can I return them? Also, can you ship a cardamom bun to another state?"

1. The harness starts the message list with two messages. The system message is the brief you met above. The user message is the customer’s question. At this moment neither file has been opened. The model cannot yet see the policy.
2. The harness calls the model. A cooperative model does not invent a return window. It proposes a tool call: `read_file`, with `path` set to `policy.md`. The file is still closed, because a proposal is only a request.
3. The harness checks the request against the contract in the next section, and then the function `read_file`, in `labs/common/tools.py`, opens the file. The text comes back with a header on the first line, `PATH: docs/policy.md`, so the source of the text is visible. The harness appends that text as a tool message, tied to the same call identifier the model used.
4. The harness calls the model again. The message list now contains the policy. The model can answer from what it was shown. Opened coffee is final sale. Pastries are not shipped. Both claims should carry the citation `(docs/policy.md)`, because the brief asked for the path and the observation supplied it.
5. The reply contains no further tool call. The harness treats the text as the customer-facing answer and stops. The stop tag for this path is `final`.

The first request may be the wrong file, and the loop is built to survive that. Suppose the model asks for `faq.md` while it is looking for a shipping rule. The FAQ says that returns and shipping live in the policy, and it does not restate the shipping rule. That result is still an observation. The model can read it, ask for `policy.md` on the next turn, and only then state the rule. The recovery is why this program is a loop. An instruction that always opened the policy would have no next step when the first file was the wrong one. When you write the program, you do not yet know which file the next question will need.

A question you will meet again in Chapter 3 needs both files at once. The local delivery fee lives only in the policy: $4.50, free at $35 and above, Tuesday through Friday, within 3 miles. The closed day lives only in the FAQ: Monday. The same loop handles that question without a new branch in your code. The model may call `read_file` twice, the harness returns two observations, and the model then writes the answer. Two reads and one reply are still the same program.

## Four moments: perceive, reason, act, and observe

The same loop can be described as four moments. The names are perceive, reason, act, and observe. They are a teaching order for one turn. They are not four separate programs. The harness performs the calling, the file access, and the bookkeeping. The model participates by reading the messages it is given and by producing the next reply.

**Perceive.** To perceive, in this chapter, means to take in the message list. The list holds the system brief, the customer’s question, and every tool result the harness has appended so far. The model perceives that list. It does not perceive the filesystem. A fact that is absent from the messages is absent from the model’s world on this turn. If the model then states the fact anyway, it is drawing on habit from training, which is the behavior Chapter 1 put on the screen. A further sentence in the prompt leaves that world unchanged. Copying a document into the message list is what lets the model perceive the document.

**Reason.** To reason, here, means to call the model and to read the object that comes back. The call is a request to a server that holds the weights. You do not inspect those weights, and you do not need to. You inspect the reply. The reply may contain assistant text, one or more tool calls, or both. In this lab, "reasoning" names that choice as it appears in the reply. You can see what the model asked to do. You cannot see a private chain of thought unless the model writes one into the text, and the loop does not depend on one being written.

**Act.** To act means that your code runs the tool the model requested. The model proposes a read, and the function `read_file` performs it. This split is the security boundary later chapters will tighten. In this chapter the boundary is concrete and modest: the path must stay inside the shop’s documents directory. A request that tries to step outside that directory becomes an error string, which is the next moment, and it does not become an action on the disk.

**Observe.** To observe means to append the tool’s result to the message list, and then to call the model again. The observation is data, including the case where the data is bad news. When the path was illegal or the file was missing, the result is a string that begins with `ERROR:`. The loop continues, and the model gets a chance to recover, because it can read the error. An exception that kills the process is a lost observation, because the model cannot correct a crash it was never shown. For that reason the tool in this chapter returns failures as text, and it lets the loop continue.

## A tool is a contract

Before the model can propose a tool call, the harness has to tell the model what tools exist, what arguments they take, and what a result will look like. That description is a contract. You should be able to write its four parts down before you implement the tool. The description tells the model what to expect, and the function is what makes the contract true. A sentence in the description cannot, by itself, keep a path inside a folder.

The contract for the only tool in this lab has four parts.

- **Name.** The tool is called `read_file`. That is the only name the dispatcher accepts. If the model asks for `send_email`, or for a refund, the harness does not improvise an action. It returns an error that says only `read_file` is available.
- **Arguments.** The tool takes one argument, a string named `path`, relative to the documents directory. In this lab the files that exist are `policy.md` and `faq.md`.
- **Returns.** On success the tool returns the file’s text as UTF-8. The first line is a header such as `PATH: docs/policy.md`. The header gives the model something true to copy when it cites a source.
- **Errors.** On failure the tool returns a string that begins with `ERROR:`. A missing file, a path that climbs out with `..`, an absolute path, a hidden name, and a file that is not valid UTF-8 text all take this shape. The process does not crash. The loop continues, and the error becomes the next observation.

The object the server actually receives is `READ_FILE_TOOL`, in `labs/common/tools.py`. Its description is documentation written for the model. It says that `policy.md` holds returns, shipping, damage, and local delivery, and that `faq.md` holds hours, location, menu prices, and allergens. That guidance is part of the harness, because it influences which file the model is likely to request. The function remains free to receive some other path, and the function then decides what happens.

The function refuses several kinds of path, and it returns the refusal as text.

- Any path that contains `..`, including an attempt to reach an environment file such as `../.env`.
- An absolute path, such as `/etc/passwd`.
- A hidden name, such as `.env`.
- A symbolic link inside the documents folder whose target resolves outside that folder.

When the file is simply missing, the error names the markdown files that do exist, so the next turn has something to recover with. A typical result says that the requested name was not found, and then lists `faq.md` and `policy.md`.

Arguments receive the same treatment. Some providers send `function.arguments` as a JSON string. Some local stacks send a dictionary. The helper `parse_arguments` accepts both. If the string is not valid JSON, the harness does not crash. It appends an `ERROR:` result that shows the expected shape, an object with a `path` such as `policy.md`, and the loop continues inside the step budget. An unknown tool name is handled in the same way. The model sees the mistake and may try again.

Successful reads are also bounded. The harness keeps at most 12,000 characters, a limit named `MAX_FILE_CHARS`. The two shop files are far smaller, so a normal run will not meet the limit. The cap is there so that a later, longer document cannot silently fill the model’s window. When the harness does cut a file, it marks the cut with the words `[truncated by harness]`. The observation stays honest about what the model was shown. A fragment presented as the whole file would teach the model a false picture of the shop.

The dispatcher is a closed set. The function `_dispatch` either calls `read_file` or returns an unknown-tool error. There is no evaluation of model text as code, no shell, and no rule that opens whatever path the model supplied from the root of the repository. The documents directory is an argument to `run_file_agent`. This chapter’s script passes `labs/ch02-your-first-loop/docs`. Chapter 3’s script passes that same directory. Aiming the tool at the rest of the repository would mean editing the harness, because it would change what the concierge is allowed to touch.

`read_file` is a sensor. It lets the model perceive one folder, after your program has copied that folder’s text into the conversation. Later chapters add tools that change the world, such as a cart or a ticket, and the same four-part contract still applies. A tool needs a name, a set of arguments, a success result, and an error result the loop can carry back to the model. If a failure never re-enters the message list, the model has no way to repair it on the next turn.

You can see the directory limit without calling a model. The lab notes give the command. The result should be a line that begins with `ERROR:`, and the contents of an environment file should remain unseen.

## Four ways the loop is allowed to stop

A loop that cannot stop is a stuck process. On a hosted model it is also an open bill. The model cannot be relied on to end the work by itself, so the harness keeps that promise. The field `stopped` on the result records which reason fired. Read that tag before you judge the prose. A smooth paragraph and a stopped process can look similar on the screen, and they are different events.

```mermaid
flowchart TD
  call[Call the model]
  choice{What did the model return}
  final[Stop as final]
  tokens[Stop as max tokens]
  repeat{Third identical tool call}
  repeated[Stop as repeated call]
  act[Run the tool]
  budget{Six model calls already used}
  maxsteps[Stop as max steps]
  call --> choice
  choice -->|text only| final
  choice -->|truncated text| tokens
  choice -->|tool call| repeat
  repeat -->|yes| repeated
  repeat -->|no| act
  act --> budget
  budget -->|yes| maxsteps
  budget -->|no| call
```

*Figure 2.2. The four stops. "Final" means the model stopped requesting tools.*

**Final.** The model returned a message with no tool calls. The harness treats the assistant text as the customer-facing answer and returns it. This is the success path, and it is also the path on which the model skipped the tool and answered from memory. The word `final` means that the model stopped calling tools. Whether the answer is true is a separate question, and you settle it by reading the trace and the file. A polished paragraph with an empty tool log is one event. A paragraph that arrived after `policy.md` was read is another. The trace is what tells them apart.

**Maximum steps.** The budget is six calls to the model, the constant `DEFAULT_MAX_STEPS`. The count is in model calls, not in tool calls. A question about this shop needs at most two reads. Six leaves room for a bad path, an error result, and a retry. When the budget is spent, `run_file_agent` returns a stop message and does not compose a customer-facing paragraph from the trace. Writing that paragraph inside the harness would hide the overrun. The lab still prints the trace, so you can see the reads that did happen.

**Repeated call.** The same tool name with the same JSON arguments may run twice. The second result includes a note that the file was already read and that an answer is now due. A third identical call stops the loop. Without that rule, a model that rereads `policy.md` forever would spend the whole budget and say nothing new. The signature includes the arguments, so a read of `policy.md` followed by a read of `faq.md` counts as two different observations. The stop fires when the model repeats itself, which is the case where another call would teach it nothing new.

**Maximum tokens.** If a turn ends because it hit the length limit, and that turn contains no tool call, the harness stops and labels the reason `max_tokens`. The limit, `MAX_TOKENS`, lives in `labs/common/client.py` and is set to 800. A limit that is too small cuts a reply in the middle of a sentence. On some providers it can also cut the JSON of a tool call’s arguments. That case usually appears on the next observation as an error about invalid JSON, and the model may try again until the step budget ends. If you see truncated arguments, you raise `MAX_TOKENS`. That change belongs to the harness. It is separate from the provider switch that Chapter 3 introduces.

The lab script prints the stop tag after the answer, together with the number of model calls:

```text
--- stop: final after 2 model call(s) ---
```

When you compare two models in Chapter 3, compare this line as well as the prose.

## Citations, and how to check them

A grounded answer shows where its shop facts came from. The tool result begins with a path header:

```text
PATH: docs/policy.md
```

The system prompt tells the model to carry that path into the answer, in parentheses, for example `(docs/policy.md)`. A fee, an hour, or a return window with no path is not yet a grounded answer, even when the sentence happens to match the file. You can check the match only because the path tells you which file to open. Treat the citation as that path, and open the file before you accept the sentence.

The script `file_agent.py` prints a soft note when the final text does not contain the substring `docs/`. That note is feedback for you, the person running the exercise. It does not call the model again. Because it looks only for a substring, a model can satisfy it by printing a path it never read. Chapter 11 separates a real checker from the model that drafts the answer. The work in this chapter is the simpler habit underneath that later checker. You open the cited file, and you confirm that the sentence is actually in it.

Use the shop’s own text as the answer key when you grade a run by hand.

- **Opened coffee**, in `docs/policy.md`: final sale.
- **Unopened coffee**, in `docs/policy.md`: 14 days, a receipt, Hearth card credit, and no cash refund.
- **Shipping a cardamom bun**, in `docs/policy.md`: pastries are not shipped.
- **Coffee shipping under $40**, in `docs/policy.md`: $6.00, inside the United States only, packed within two business days. Orders of $40 or more ship free.
- **Local delivery**, in `docs/policy.md`: $4.50, free at $35 and above, Tuesday through Friday, within 3 miles.
- **Closed day**, in `docs/faq.md`: Monday.
- **Hours**, in `docs/faq.md`: Tuesday through Friday, 7:30–15:30; Saturday and Sunday, 8:00–16:00.
- **Cardamom-bun allergens**, in `docs/faq.md`: wheat, butter, and almonds. There is no nut-free preparation area.
- **Guest network**, in `docs/faq.md`: `hearth-guest`.
- **Wi-Fi password**: neither file. It is printed on the paper receipt. An invented password is a failure even when a path is cited.

Two traps are worth meeting on purpose, and the lab includes both questions.

The first trap is the difference between opened and unopened coffee. The policy states both rules, one after the other. A model that has read the file can still apply the unopened rule — fourteen days, a receipt, store credit — to a bag the customer has already opened. The trace will show that the file was seen. You still compare the claim with the file, because a successful read shows only that the document was available. The sentence itself remains to be checked.

The second trap is silence. Asked for the Wi-Fi password, a sound trace reads `faq.md`, may report the network name `hearth-guest`, and then declines to invent a password. A weak trace prints a plausible password, and sometimes cites the FAQ as though the file’s silence were a source. Asked whether the café sells live crabs, the files are silent in the same way. The grounded reply says that the documents do not say. A made-up menu item is a miss. A concierge that feels required to answer every question will fail these cases by design. The brief tells the model to admit ignorance, and the files give it nothing else to say.

Citations are harness work in two places, and it is worth keeping the places separate. Your code adds the `PATH:` header, so the observation carries a source. The instruction to copy that path into the answer is a sentence in the prompt, which the model may ignore. When the model ignores the instruction, you have a feedback item in the sense of Chapter 1: something other than the drafting model has noticed a miss. You may revise a sentence in the prompt later. For this chapter, write the miss down so the next run can be compared with this one.

## How to read a run

Once a file can be opened, the failures you should watch for become more specific. In Chapter 1 the model could invent a shop rule or decline to guess, and that was the whole range, because no file was available. In this chapter the model can also skip the file, open the wrong file, misquote the right file, or keep reading after an answer was already possible. The trace is how you tell those cases apart. A demonstration that shows only the customer-facing paragraph hides which of them occurred.

You will commonly see one of the following.

- **The model skips the tool.** The stop is `final`, and the tool log is empty. The paragraph may be fluent and wrong. It is Chapter 1, running inside a Chapter 2 program. The harness allows the skip, because a field that forces a tool call is not portable across the providers in Chapter 3. Record the empty trace. Treat it as model behavior until you have asked the same question of a model that does call tools.
- **The model reads the wrong file, then recovers.** An error, or a file that lacks the fact, is followed by a second read. That recovery is the loop earning its place, even when the first choice was clumsy.
- **The model reads the right file and still misquotes it.** The opened-coffee trap above is the usual example. The trace shows that the document was seen. You still compare the sentence with the file.
- **The model cites a path it did not read.** The soft check looks for the letters of a path. A review that stops at that check will accept a path the trace never opened, so you still open the file and compare the sentence with the text.
- **The loop spins.** Repeated reads of the same file, or a walk that never settles, should hit a stop you can name: `repeated_call` or `max_steps`. In this design the harness does not then compose a smooth closing paragraph. The stop message is the result, and the trace is the work that happened.
- **The model offers a refund, a shipment, or an email.** The tool list contains no such action. The offer is only a sentence in the reply, and nothing in the log moved money or mail. It is the action-boundary failure from Chapter 1, now with a trace beside it.

From one real question, write down four things beside the paragraph the customer would see.

- Which documents were opened, and whether each result began with `PATH:` or with `ERROR:`.
- The stop reason and the step count: `final`, `max_steps`, `repeated_call`, or `max_tokens`.
- Whether each shop fact in the answer appears in the cited file, with the file’s line next to the model’s line.
- What the program did when the documents are silent. The Wi-Fi password, and a product the shop does not sell, are the probes for that case.

Those notes also say where a later change belongs. An empty trace points at the model, or at a contract the model is not using. Rewriting the concierge’s persona, while leaving the tool list as it is, will leave the file closed. A full trace whose sentences still drift points at feedback, because an uncited or misquoted claim is still being accepted. A trace that showed a tool you never meant to offer would mean the contract is too wide, and narrowing it would be a change to the harness.

The shared tests in `labs/common/test_harness.py` cover the directory limit, invalid arguments, unknown tools, the step cap, and the repeated-call stop. They do not contact a model server. The lab notes say how to run them.

## Lab

Answer the return question and the shipping question from the shop documents, and require a path citation on each shop fact. From one real run, record the trace, the stop, the step count, and whether each shop fact appears in the cited file. An empty trace is itself the observation. The harness did not force a tool call.

Setup, the command, the further questions, and the checks that run without a model are in the [Chapter 2 lab](../../labs/ch02-your-first-loop/README.md).

The loop is what opens a file, keeps the path inside one directory, returns errors as text the model can read, and refuses to run forever. The prompt tells the model which files exist and how to cite them. A working read still needs you, or a later checker, to confirm that the citation matches the file. The next chapter keeps this harness still and changes only the model, so you can see which part of the answer moved with the weights.
