# Tutorial 7. The web as an untrusted sensor

## Motivation

A supplier page can tell you a wholesale price. It can also tell the concierge to change a shop price or to start a charge. Those sentences arrive in the same fetch. If the agent treats the page as a manager, a public page becomes a way to operate the shop. This lesson teaches the page as a sensor: useful to quote, unsafe to obey. The shop’s own prices, counts, and charges stay with the shop’s own tools.

## What this tutorial is about

The web, in this lesson, means one page the program is allowed to fetch. The page is served from a file in the repository, so the lesson does not depend on the public internet. The text that comes back is marked as untrusted. Untrusted text is data from outside the shop. The agent may quote it as a claim. The agent may not treat it as an instruction that adds tools, changes a Hearth Lane price, or starts a payment.

You will learn to allow one address and to refuse every other address. You will learn to keep the shelf count on the shelf tool. A page can mention a carton. The count the shop believes is the one in the database.

## How you will get there

The notebook adds a fetch tool for that single supplier page. You ask for the case price the page states, and you ask for what the shelf shows. The result of the fetch is labeled so a person can see the boundary. The answer may repeat the page’s price as the page’s claim. The shelf reading stays a separate tool result.

You will read the label, the claim, and the shelf line as three different things. The hands-on steps are in the notebook [7-web-browse](7-web-browse.ipynb).

## Additional things

An allow-list is the boundary on where the tool may go. A request for any other address is an error. A later tutorial takes the same page, which also tries to issue orders, and shows that the path check and the action gate still hold when the model is persuaded. The label in this lesson is the start of that boundary. The gate is the part that enforces it.

Quoting a page means naming it as a source. A sentence that sounds like the shop’s own price, with the page’s number dropped in silently, has lost the boundary. Chapter 8 is the book’s treatment of fetching, grounding a quote, and the ways a page can try to give orders.

The café in these files is fictional. The supplier page is a local practice file.

## Sources and references

- [Chapter 8: Browsing the web](../../chapters/ch08-browsing-the-web/README.md), and the lab [labs/ch08-browsing-the-web](../ch08-browsing-the-web).
- The boundary is hardened in [11-prompt-injection.md](11-prompt-injection.md) and in [Chapter 21: Prompt injection and untrusted data](../../chapters/ch21-prompt-injection-and-untrusted-data/README.md).
- The previous lecture is [6-skills.md](6-skills.md). The series map is in [README.md](README.md).
