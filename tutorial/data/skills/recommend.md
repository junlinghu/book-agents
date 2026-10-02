# Recommend a jar

## When to use

A customer asks what to buy, especially with an allergy or a favorite already on file.

## Steps

1. Load this skill. Do not paste the catalog into the system prompt.
2. Call get_preference with that customer's name before you name a jar. One name returns one entry. Do not pass a filename.
3. Call get_store_fact for the allergens topic. That result is the source for what a jar contains. Do not pass a filename.
4. Call query_catalog for the jar you are about to name. Stock and price come from that row. This skill is not a catalog. Do not pass SQL.
5. Apply an allergy the customer actually has on file. Use the allergens topic to decide which jars to skip. Do not skip a jar that topic does not mention.
6. If the catalog has no jar that fits, say so. Do not invent a product.

## Refuse

Do not promise a sesame-free kitchen.
Do not invent a discount code.
Do not charge a card, cancel an order, or email the customer.
