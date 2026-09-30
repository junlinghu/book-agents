#!/usr/bin/env python3
"""Create shop.db from data/seed.sql."""

from __future__ import annotations

import sqlite3
from pathlib import Path

LAB = Path(__file__).resolve().parent
DB = LAB / "shop.db"


def main() -> int:
    with sqlite3.connect(DB) as conn:
        conn.executescript((LAB / "data" / "seed.sql").read_text(encoding="utf-8"))
    print(f"Wrote {DB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
