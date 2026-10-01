# Tutorial 7. A page from the supplier

## Motivation

The agent can follow a written procedure, using memory, notes, documents, and the shelf, and it can stop when the loop says the work is finished. Every fact it has used so far lives in this repository, in files the shop controls. What it still cannot do is read a page that someone else wrote. A supplier’s wholesale price is useful at the counter, and the same page can contain sentences that try to give orders: charge a card, read a secret, change the price of a bun. We add a single page now, fetched as a reading and marked as untrusted, before the checker and the gate. Tutorial 11 will test that the mark is a boundary the program enforces. This tutorial is where the agent first meets text it did not author.

## What this tutorial is about

This tutorial treats a web page as a sensor, a reading that reports something and leaves the shop unchanged. The only page on offer is a local stand-in for Mill and Birch, the café’s supplier, so the lesson does not depend on the public internet. The page names a wholesale price for oat milk and for the house blend. It also contains instructions aimed at the agent.

You will learn to allow only that one address, so that any other address comes back as an error. You will learn to wrap the returned text so a person can see where the page begins, and to keep the shelf count in the shelf. The price may be quoted as a claim the page made. The orders on the page do not become tools, and they do not change a Hearth Lane price.

## How you will get there

The notebook adds a fetch action for that one address. You ask what wholesale oat-milk price the page claims, and you ask that the claim stay separate from the shelf. The agent fetches the page and reads the shelf. The printed answer quotes the price and marks the page as untrusted. The record of the run shows the fetch and the shelf reading, and it does not show a charge. You can hold the answer next to the page and see which sentence was a price and which sentences were orders the agent left alone.

## Additional things

An allow-list is the whole of the network policy in this lesson. There is no open client for the public web. The page in this folder is a fixture, so the lesson does not depend on a live site, a changing layout, or a blocked request. The page’s attempt to give orders is a preview of what tutorial 11 calls prompt injection. That later notebook runs the bad proposals through the file boundary and the action gate, so the result does not depend on the model happening to be polite.

The shelf count still comes from the database you met in tutorial 2. A sentence on a supplier page is a claim about a price. It is a poor source for how many cartons are on hand, which is why this notebook reads both and keeps them apart. The café in these files is fictional. Leave private files alone.

## Sources and references

- The supplier page is [data/pages/mill-and-birch.html](data/pages/mill-and-birch.html). `fetch_page` is in [common/web.py](common/web.py).
- The previous lecture is [6-skills.md](6-skills.md). The notebook is [7-web-browse.ipynb](7-web-browse.ipynb). The series map is in [README.md](README.md).
