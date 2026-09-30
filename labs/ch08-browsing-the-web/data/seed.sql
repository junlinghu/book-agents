-- Register prices for the Chapter 8 lab.
-- Amounts are cents and match labs/ch02-your-first-loop/docs/faq.md.
-- The static board in site/shop.html is allowed to disagree.

DROP TABLE IF EXISTS products;
CREATE TABLE products (
  sku TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  price_cents INTEGER NOT NULL
);

INSERT INTO products (sku, name, price_cents) VALUES
  ('house-espresso', 'House espresso', 350),
  ('pour-over', 'Pour-over', 425),
  ('cardamom-bun', 'Cardamom bun', 475),
  ('rye-porridge', 'Rye porridge', 800);
