#!/usr/bin/env python3
"""Create shop.db from data/seed.sql. The SQL server reads this file."""

from __future__ import annotations

import sqlite3
from pathlib import Path

LAB = Path(__file__).resolve().parent
SEED = LAB / "data" / "seed.sql"
DB = LAB / "shop.db"


def main() -> int:
    with sqlite3.connect(DB) as conn:
        conn.executescript(SEED.read_text(encoding="utf-8"))
    print(f"Wrote {DB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
