# Tutorial 7. Checking a cart

## Motivation

The seller can quote a page as a claim someone else made. It can also sound sure while the quantity is wrong. A note can say to ship a thousand jars, and a fluent paragraph will repeat the number. What the seller still cannot do is separate a proposed cart from a check that reads stock itself. We add that checker now, before we grade the seller and before we let it write anything down, because a purchase that files a note should already know which carts the checker will accept.

## What this tutorial is about

`verify_cart` is a second step. The rules are in the program. It loads the catalog row itself. The quantity it accepts is at least 1 and not more than stock. An item with `shippable` false cannot ship. A destination has to be a US state such as Ohio when the cart ships. A missing citation is a finding. You will see a bad proposal rejected and a good one accepted before the model is involved, and you will then see the agent call the same checker. The cart you trust is the one the checker accepted.

## How you will get there

The notebook scores three carts with no model in the path. One asks for 100 jars of chili oil and cites nothing. The checker rejects it and names the stock. One is a single jar to Ohio with a citation. The checker accepts it. One ships fresh labneh. The checker rejects it as not shippable. The customer then asks the seller to check the good cart. The tool log shows `verify_cart` and `accepted`.

## Additional things

A checker that trusts the proposer's arithmetic is a second copy of the proposal. The value of this one is that it recomputes the limit from the database you met in tutorial 2. Tutorial 11 gives the same split to two roles, and an origin note that says to ship a thousand jars fails there for the same reason. Tutorial 15 uses the checker before any order note is written.

The store in these files is fictional.

## Sources and references

- The checker is [common/verify.py](common/verify.py).
- The previous lecture is [6-web-browse.md](6-web-browse.md). The notebook is [7-verification.ipynb](7-verification.ipynb). The series map is in [README.md](README.md).
