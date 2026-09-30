-- Register for the Chapter 9 contract test.
-- Cents match labs/ch02-your-first-loop/docs/faq.md.

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
