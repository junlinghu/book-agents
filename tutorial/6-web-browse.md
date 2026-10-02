# Tutorial 6. One untrusted page

## Motivation

The seller can read the store's own files. A customer will also ask what a supplier or an origin page says. That page is not the catalog. The Calabrian mill page, in this lesson, claims a mill price of $6.40 a jar and, in the same breath, tells the seller to charge a card and ignore the store. A fetch that treats those sentences as orders has confused a sensor with a boss. We add one allow-listed page now, marked untrusted, before a checker and a gate exist to refuse the rest of what the page demands.

## What this tutorial is about

`fetch_page` reads a local copy of one URL. There is no open web client. Any other URL is an error. The result starts with `UNTRUSTED PAGE TEXT`. The customer asks for the mill's claimed price and asks to keep it separate from the Harbor Jar price. The shop price comes from `query_catalog`. The mill price is quoted as a claim. The page's demand to charge a card is not a tool call.

## How you will get there

The notebook prints the allow-listed URL, then runs the customer's question. You should see `fetch_page` and `query_catalog` in the tool log, `$6.40` in the answer as the mill's figure, and no `charge_card`. Tutorial 10 runs the same page through the gate on purpose. This lesson only establishes that the page is data.

## Additional things

Marking a page "untrusted" is a label until some later function enforces it. The label is still worth printing, because the next reader of the trace can see which sentences were someone else's. Do not paste a real customer's mail into this loop, and do not point `fetch_page` at a page of real people's data. The mill page is fictional.

## Sources and references

- The page is [data/pages/calabrian-mill.html](data/pages/calabrian-mill.html). The tool is [common/web.py](common/web.py).
- The previous lecture is [5-skills.md](5-skills.md). The notebook is [6-web-browse.ipynb](6-web-browse.ipynb). The series map is in [README.md](README.md).
