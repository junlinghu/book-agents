#!/usr/bin/env python3
"""Mock checkout for Hearth Lane Café.

Chapter 18 lab. A confirmed quote inserts one ``orders`` row in a local
SQLite file. No card number is stored, and ``payment_status`` stays
``mock_not_charged``. There is no payment network in this process.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.autonomy import approval_token, decide, format_decision  # noqa: E402

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
VAR = Path(__file__).resolve().parent / "var"
DB_PATH = VAR / "shop.db"
POLICY_PATH = ROOT / "labs" / "ch02-your-first-loop" / "docs" / "policy.md"
PAN = "4242424242424242"

SHIP_DAYS = {"Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
DELIVERY_DAYS = {"Tuesday", "Wednesday", "Thursday", "Friday"}
FREE_SHIP_CENTS = 4000
SHIP_FEE_CENTS = 600
FREE_DELIVERY_CENTS = 3500
DELIVERY_FEE_CENTS = 450


def money(cents: int) -> str:
    return f"${cents // 100}.{cents % 100:02d}"


def load_catalog(path: Path = CATALOG_PATH) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["items"])


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stock (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price_cents INTEGER NOT NULL,
            on_hand INTEGER NOT NULL,
            kind TEXT NOT NULL,
            shippable INTEGER NOT NULL,
            deliverable INTEGER NOT NULL,
            pickup INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            channel TEXT NOT NULL,
            destination TEXT NOT NULL,
            lines_json TEXT NOT NULL,
            subtotal_cents INTEGER NOT NULL,
            fee_cents INTEGER NOT NULL,
            total_cents INTEGER NOT NULL,
            status TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            confirmed_by TEXT NOT NULL
        )
        """
    )
    return conn


def seed(conn: sqlite3.Connection, items: list[dict] | None = None) -> None:
    """Load the catalog when stock is empty. ``--reset`` deletes the file first."""
    count = conn.execute("SELECT COUNT(*) AS n FROM stock").fetchone()["n"]
    if count:
        return
    for item in items if items is not None else load_catalog():
        conn.execute(
            """
            INSERT INTO stock (
                sku, name, price_cents, on_hand, kind,
                shippable, deliverable, pickup
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["sku"],
                item["name"],
                int(item["price_cents"]),
                int(item["stock"]),
                item["kind"],
                int(bool(item["shippable"])),
                int(bool(item["deliverable"])),
                int(bool(item["pickup"])),
            ),
        )
    conn.commit()


def shipping_fee_cents(subtotal_cents: int) -> int:
    """Coffee under $40 ships for $6.00. $40 or more ships free."""
    if subtotal_cents >= FREE_SHIP_CENTS:
        return 0
    return SHIP_FEE_CENTS


def delivery_fee_cents(subtotal_cents: int) -> int:
    """Local delivery is $4.50, and free at $35 or more."""
    if subtotal_cents >= FREE_DELIVERY_CENTS:
        return 0
    return DELIVERY_FEE_CENTS


def lookup(conn: sqlite3.Connection, sku: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM stock WHERE sku = ?", (sku,)).fetchone()


def quote(conn: sqlite3.Connection, request: dict) -> dict | str:
    """Price a cart from stock and the shop rules. Does not write an order."""
    channel = request.get("channel")
    lines_in = request.get("lines")
    if channel not in {"ship", "local_delivery", "pickup"}:
        return "ERROR: channel must be ship, local_delivery, or pickup."
    if not isinstance(lines_in, list) or not lines_in:
        return "ERROR: lines must list at least one sku."

    priced: list[dict] = []
    subtotal = 0
    for line in lines_in:
        sku = str(line.get("sku", ""))
        qty = line.get("qty", 0)
        if not isinstance(qty, int) or qty < 1:
            return f"ERROR: qty for {sku or '(missing sku)'} must be a positive integer."
        row = lookup(conn, sku)
        if row is None:
            return (
                f"ERROR: {sku!r} is not in the catalog. "
                "The model does not get to invent a price."
            )
        if qty > row["on_hand"]:
            return (
                f"ERROR: {sku} has {row['on_hand']} on hand, not {qty}. "
                "No order written."
            )
        if channel == "ship" and not row["shippable"]:
            return (
                f"ERROR: {row['name']} is not shipped "
                "(docs/policy.md). No quote and no order."
            )
        if channel == "local_delivery" and not row["deliverable"]:
            return (
                f"ERROR: {row['name']} is not available for local delivery "
                "(docs/policy.md). Hot drinks stay at the counter."
            )
        if channel == "pickup" and not row["pickup"]:
            return f"ERROR: {row['name']} is not available for pickup."
        line_total = int(row["price_cents"]) * qty
        subtotal += line_total
        priced.append(
            {
                "sku": sku,
                "name": row["name"],
                "qty": qty,
                "unit_price_cents": int(row["price_cents"]),
                "line_total_cents": line_total,
            }
        )

    destination = str(request.get("address", "")).strip()
    country = str(request.get("country", "")).strip()
    day = str(request.get("day", "")).strip()
    if channel == "ship":
        if country != "US":
            return "ERROR: coffee ships inside the United States only (docs/policy.md)."
        if "po box" in destination.lower():
            return "ERROR: the café does not ship to PO boxes (docs/policy.md)."
        if day == "Monday":
            return "ERROR: nothing ships on Monday, when the café is closed (docs/policy.md)."
        if day not in SHIP_DAYS:
            return "ERROR: ship day must be a named day, and Monday does not ship."
        fee = shipping_fee_cents(subtotal)
    elif channel == "local_delivery":
        miles = request.get("miles")
        if not isinstance(miles, (int, float)) or miles < 0 or miles > 3:
            return "ERROR: bike delivery covers addresses within 3 miles (docs/policy.md)."
        if day not in DELIVERY_DAYS:
            return (
                "ERROR: local delivery runs Tuesday through Friday only "
                "(docs/policy.md)."
            )
        fee = delivery_fee_cents(subtotal)
    else:
        fee = 0

    return {
        "channel": channel,
        "country": country,
        "address": destination,
        "day": day,
        "miles": request.get("miles"),
        "lines": priced,
        "subtotal_cents": subtotal,
        "fee_cents": fee,
        "total_cents": subtotal + fee,
        "payment_status": "mock_not_charged",
    }


def checkout_arguments(quoted: dict) -> dict:
    """The object the confirm token binds. Payment fields are not accepted."""
    return {
        "channel": quoted["channel"],
        "country": quoted["country"],
        "address": quoted["address"],
        "day": quoted["day"],
        "lines": [
            {
                "sku": line["sku"],
                "qty": line["qty"],
                "unit_price_cents": line["unit_price_cents"],
            }
            for line in quoted["lines"]
        ],
        "subtotal_cents": quoted["subtotal_cents"],
        "fee_cents": quoted["fee_cents"],
        "total_cents": quoted["total_cents"],
        "payment_status": "mock_not_charged",
    }


def place(conn: sqlite3.Connection, quoted: dict, confirmed_by: str) -> dict:
    """Insert the order and decrement stock in one transaction."""
    destination = quoted["address"] or quoted["channel"]
    try:
        conn.execute("BEGIN")
        for line in quoted["lines"]:
            cursor = conn.execute(
                """
                UPDATE stock
                SET on_hand = on_hand - ?
                WHERE sku = ? AND on_hand >= ?
                """,
                (line["qty"], line["sku"], line["qty"]),
            )
            if cursor.rowcount != 1:
                conn.rollback()
                return {
                    "ok": False,
                    "error": f"ERROR: {line['sku']} stock changed before checkout. No order written.",
                }
        cursor = conn.execute(
            """
            INSERT INTO orders (
                created_at, channel, destination, lines_json,
                subtotal_cents, fee_cents, total_cents,
                status, payment_status, confirmed_by
            ) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quoted["channel"],
                destination,
                json.dumps(quoted["lines"], sort_keys=True),
                quoted["subtotal_cents"],
                quoted["fee_cents"],
                quoted["total_cents"],
                "placed",
                "mock_not_charged",
                confirmed_by,
            ),
        )
        order_id = int(cursor.lastrowid)
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        return {"ok": False, "error": f"ERROR: checkout failed ({exc}). No order kept."}
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return {"ok": True, "order": dict(row)}


def format_receipt(order: dict) -> str:
    lines = json.loads(order["lines_json"])
    rendered = []
    for line in lines:
        rendered.append(
            f"  {line['qty']} × {line['name']} @ {money(line['unit_price_cents'])}"
        )
    body = "\n".join(rendered)
    return (
        "--- receipt ---\n"
        f"order_id: {order['id']}\n"
        f"channel: {order['channel']}\n"
        f"destination: {order['destination']}\n"
        f"lines:\n{body}\n"
        f"subtotal: {money(order['subtotal_cents'])} ({order['subtotal_cents']} cents)\n"
        f"fee: {money(order['fee_cents'])} ({order['fee_cents']} cents)\n"
        f"total: {money(order['total_cents'])} ({order['total_cents']} cents)\n"
        f"status: {order['status']}\n"
        f"payment_status: {order['payment_status']}\n"
        f"confirmed_by: {order['confirmed_by']}\n"
        "card_charged: no\n"
        "network: none"
    )


def _scene(title: str, result: str) -> list[str]:
    return [f"[{title}]", f"    result={result}", ""]


def coffee_request(qty: int, day: str = "Tuesday", address: str = "14 Oak St, Columbus") -> dict:
    return {
        "channel": "ship",
        "country": "US",
        "address": address,
        "day": day,
        "lines": [{"sku": "house-coffee-12oz", "qty": qty}],
    }


def run_story(conn: sqlite3.Connection, confirmed_token: str | None) -> str:
    lines: list[str] = [
        "Hearth Lane mock checkout",
        "model=scripted (no model server on this path)",
        "payments=mock_not_charged",
        "network=none",
        "",
    ]

    for sku in ("house-coffee-12oz", "cardamom-bun"):
        row = lookup(conn, sku)
        if row is None:
            lines.extend(_scene(f"lookup {sku}", "ERROR: missing from stock"))
            continue
        lines.extend(
            _scene(
                f"lookup {sku}",
                (
                    f"{row['name']} {money(row['price_cents'])} "
                    f"on_hand={row['on_hand']} shippable={bool(row['shippable'])} "
                    f"deliverable={bool(row['deliverable'])}"
                ),
            )
        )

    bun = quote(
        conn,
        {
            "channel": "ship",
            "country": "US",
            "address": "14 Oak St, Columbus",
            "day": "Tuesday",
            "lines": [{"sku": "cardamom-bun", "qty": 1}],
        },
    )
    lines.extend(_scene("quote ship cardamom-bun", bun if isinstance(bun, str) else "unexpected quote"))

    monday = quote(conn, coffee_request(1, day="Monday"))
    lines.extend(_scene("quote ship coffee Monday", monday if isinstance(monday, str) else "unexpected quote"))

    one = quote(conn, coffee_request(1))
    if isinstance(one, str):
        lines.extend(_scene("quote ship 1 coffee Tuesday", one))
        lines.append("--- summary ---")
        lines.append("orders=0")
        return "\n".join(lines) + "\n"

    payload = checkout_arguments(one)
    decision = decide("checkout", payload, confirmed_token=confirmed_token)
    lines.append("[quote ship 1 × house coffee, Tuesday, US]")
    lines.append(
        "    "
        + (
            f"subtotal={money(one['subtotal_cents'])} fee={money(one['fee_cents'])} "
            f"total={money(one['total_cents'])}"
        )
    )
    lines.append("    " + format_decision(decision).replace("\n", "\n    "))
    receipt = ""
    if decision["decision"] == "allowed" and decision["confirmed"]:
        placed = place(conn, one, "operator")
        if placed["ok"]:
            receipt = format_receipt(placed["order"])
            lines.append("    result=order inserted")
        else:
            lines.append(f"    result={placed['error']}")
    else:
        lines.append("    result=not checked out; orders unchanged")
    lines.append("")

    three = quote(conn, coffee_request(3))
    if isinstance(three, str):
        lines.extend(_scene("quote ship 3 coffee", three))
    else:
        lines.extend(
            _scene(
                "quote ship 3 coffee (not checked out)",
                (
                    f"subtotal={money(three['subtotal_cents'])} "
                    f"fee={money(three['fee_cents'])} total={money(three['total_cents'])} "
                    "status=quote_only"
                ),
            )
        )

    charge = decide(
        "charge_card",
        {"amount_cents": one["total_cents"], "card_number": PAN},
        confirmed_token=approval_token(
            "charge_card",
            {"amount_cents": one["total_cents"], "card_number": PAN},
        ),
    )
    lines.append("[charge_card]")
    lines.append("    " + format_decision(charge).replace("\n", "\n    "))
    lines.append("    result=not executed; no payment column written")
    lines.append("")

    order_count = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]
    coffee = lookup(conn, "house-coffee-12oz")
    lines.append("--- summary ---")
    lines.append(f"orders={order_count} house_coffee_on_hand={coffee['on_hand'] if coffee else 'missing'}")
    if receipt:
        lines.append(receipt)
    elif decision["tier"] == "confirm":
        lines.append(
            "To write the one-bag order, rerun with:\n"
            "  python labs/ch18-agentic-commerce/checkout.py "
            f"--reset --confirm {decision['approval_token']}"
        )
    lines.append("payment_status on a written row is mock_not_charged. No card is sent anywhere.")
    return "\n".join(lines) + "\n"


def self_check() -> int:
    import tempfile

    failures: list[str] = []

    def expect(condition: bool, label: str) -> None:
        if condition:
            print(f"ok {label}")
        else:
            failures.append(label)
            print(f"FAIL {label}")

    policy = POLICY_PATH.read_text(encoding="utf-8")
    expect("$6.00" in policy and "$40" in policy, "policy states the $6 / $40 shipping rule")
    expect("$4.50" in policy and "$35" in policy, "policy states the delivery fee")
    expect("not ship" in policy.lower() or "does not ship pastries" in policy, "policy refuses pastry shipping")
    expect(shipping_fee_cents(3999) == 600, "fee is $6.00 under $40")
    expect(shipping_fee_cents(4000) == 0, "fee is $0 at $40")
    expect(delivery_fee_cents(3499) == 450, "delivery fee under $35")
    expect(delivery_fee_cents(3500) == 0, "delivery free at $35")

    faq = (ROOT / "labs" / "ch02-your-first-loop" / "docs" / "faq.md").read_text(encoding="utf-8")
    expect("$4.75" in faq and "$3.50" in faq, "faq menu prices still match the catalog")
    catalog = {item["sku"]: item for item in load_catalog()}
    expect(catalog["cardamom-bun"]["price_cents"] == 475, "bun price matches the faq")
    expect(catalog["house-espresso"]["price_cents"] == 350, "espresso price matches the faq")
    expect("$18.00" not in faq and "12 oz" not in faq, "bag price lives in the lab catalog")

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "shop.db"
        conn = connect(db_path)
        seed(conn)
        pending = run_story(conn, None)
        expect(PAN not in pending, "story output redacts the card")
        expect("not shipped" in pending, "bun shipment is rejected")
        expect("nothing ships on Monday" in pending, "Monday ship is rejected")
        expect("orders=0" in pending, "pending checkout writes no row")
        expect("fee=$6.00" in pending, "one bag shows the $6 fee")
        expect("fee=$0.00" in pending, "three bags ship free and are not checked out")

        one = quote(conn, coffee_request(1))
        assert isinstance(one, dict)
        token = approval_token("checkout", checkout_arguments(one))
        wrong = run_story(connect(db_path), "00000000")
        # run_story on existing db: seed won't reset stock. orders still 0.
        expect("orders=0" in wrong, "wrong token writes nothing")

        fresh = Path(tmp) / "shop2.db"
        conn2 = connect(fresh)
        seed(conn2)
        approved_text = run_story(conn2, token)
        expect("orders=1" in approved_text, "matching token writes one order")
        expect("payment_status: mock_not_charged" in approved_text, "payment stays mock")
        expect("house_coffee_on_hand=19" in approved_text, "stock decrements once")
        expect(PAN not in approved_text, "receipt has no card number")
        blob = fresh.read_bytes()
        expect(PAN.encode() not in blob, "database file has no card number")
        row = conn2.execute("SELECT payment_status, status FROM orders").fetchone()
        expect(row["payment_status"] == "mock_not_charged", "row is unpaid")
        expect(row["status"] == "placed", "row is placed")
        columns = {info[1] for info in conn2.execute("PRAGMA table_info(orders)").fetchall()}
        expect("card_number" not in columns, "orders has no card column")

        abroad = quote(conn2, coffee_request(1, address="4 Rue du Bac, Paris") | {"country": "FR"})
        expect(isinstance(abroad, str) and "United States" in abroad, "international ship rejected")
        po_box = quote(conn2, coffee_request(1, address="PO Box 9, Columbus"))
        expect(isinstance(po_box, str) and "PO boxes" in po_box, "PO box rejected")

        espresso = quote(
            conn2,
            {
                "channel": "local_delivery",
                "address": "3 Mill St",
                "day": "Tuesday",
                "miles": 1,
                "lines": [{"sku": "house-espresso", "qty": 1}],
            },
        )
        expect(isinstance(espresso, str) and "Hot drinks" in espresso, "espresso is not delivered")
        bun_delivery = quote(
            conn2,
            {
                "channel": "local_delivery",
                "address": "3 Mill St",
                "day": "Tuesday",
                "miles": 2,
                "lines": [{"sku": "cardamom-bun", "qty": 1}],
            },
        )
        expect(
            isinstance(bun_delivery, dict) and bun_delivery["fee_cents"] == 450,
            "one bun delivers for $4.50",
        )
        far = quote(
            conn2,
            {
                "channel": "local_delivery",
                "address": "Far Town",
                "day": "Tuesday",
                "miles": 4,
                "lines": [{"sku": "cardamom-bun", "qty": 1}],
            },
        )
        expect(isinstance(far, str) and "3 miles" in far, "over 3 miles is rejected")
        conn2.close()
        conn.close()

    if failures:
        print(f"{len(failures)} failed")
        return 1
    print("self-check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", metavar="TOKEN")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if args.reset and DB_PATH.exists():
        DB_PATH.unlink()
    conn = connect(DB_PATH)
    try:
        seed(conn)
        print(run_story(conn, args.confirm), end="")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
