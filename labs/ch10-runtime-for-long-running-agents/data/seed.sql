-- On-hand and par for the Chapter 10 restock.
-- Draft quantity is par minus on_hand when you compute it in the runtime.

DROP TABLE IF EXISTS inventory;
CREATE TABLE inventory (
  sku TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  on_hand INTEGER NOT NULL,
  par INTEGER NOT NULL
);

INSERT INTO inventory (sku, name, on_hand, par) VALUES
  ('house-coffee', 'House coffee, 12 oz', 4, 16);
