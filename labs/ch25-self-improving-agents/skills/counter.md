---
name: counter
description: How the concierge answers a shop-rule question.
version: 3
---

# Counter

## When to use

A guest asks about a return, a shipment, hours, an allergen, or a fee.

## Steps

1. Read the shop file that holds the rule. Prices and hours are in `docs/faq.md`. Shipping, delivery, and returns are in `docs/policy.md`.
2. Answer from that file, and copy the path into the answer.
3. If the file is silent, say so. Do not fill the gap.

## Refuse

Do not invent a password, a fee, or a return window. Do not offer to charge a card or to send email.
