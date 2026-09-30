#!/usr/bin/env python3
"""Draft a counter email, and send it only after a matching confirm token.

Chapter 17 lab. The draft is a local file. Send copies that file into a
local outbox. Nothing here opens SMTP, and the From address is fixed to
the counter mailbox. This is the staff work agent: external mail can be
confirmed. It is not the customer concierge from Chapter 16, which never
sends outside the shop domain.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from labs.common.autonomy import approval_token, decide, format_decision  # noqa: E402
from labs.common.tools import read_file  # noqa: E402

DOCS = ROOT / "labs" / "ch02-your-first-loop" / "docs"
VAR = Path(__file__).resolve().parent / "var"
DRAFTS = VAR / "drafts"
SENT = VAR / "sent"

FROM_ADDRESS = "counter@hearthlane.example"
TO_ADDRESS = "sam@example.com"
SUBJECT = "Your opened bag of house coffee"

# Sentences copied from docs/policy.md. The self-check refuses to draft
# if any of them disappear from that file.
POLICY_SENTENCES = (
    "Opened coffee, ground coffee, pastries, drinks, and any food that has left the counter are final sale.",
    "Unopened retail coffee (bag valve seal intact) may be returned within 14 days of purchase.",
    "Refunds are store credit on a Hearth card only. The café does not give cash refunds.",
)


def draft_body() -> str:
    quoted = "\n".join(POLICY_SENTENCES)
    return (
        "Hello,\n\n"
        "Thank you for writing to Hearth Lane Café.\n\n"
        f"{quoted}\n\n"
        "This note cites docs/policy.md.\n\n"
        "Hearth Lane Café\n"
        "12 Hearth Lane, North Mill\n"
    )


def policy_ready() -> str | None:
    text = read_file(DOCS, "policy.md")
    if text.startswith("ERROR:"):
        return text
    missing = [sentence for sentence in POLICY_SENTENCES if sentence not in text]
    if missing:
        return "ERROR: draft quotes are not in docs/policy.md: " + missing[0]
    return None


def build_draft() -> dict:
    body = draft_body()
    # The id is a hash of the body so a second run approves the same draft.
    draft_id = "d-" + approval_token("draft_email", {"body": body})
    return {
        "draft_id": draft_id,
        "from": FROM_ADDRESS,
        "to": TO_ADDRESS,
        "subject": SUBJECT,
        "body": body,
        "status": "draft",
        "agent": "work-agent",
        "transport": "local-outbox",
    }


def send_arguments(draft: dict) -> dict:
    """The payload a person approves. ``from`` is not taken from the model."""
    return {
        "draft_id": draft["draft_id"],
        "from": FROM_ADDRESS,
        "to": draft["to"],
        "subject": draft["subject"],
        "body": draft["body"],
    }


def run_mail(confirmed_token: str | None, drafts_dir: Path, sent_dir: Path) -> str:
    if drafts_dir.exists():
        for path in drafts_dir.glob("*.json"):
            path.unlink()
    if sent_dir.exists():
        for path in sent_dir.glob("*.json"):
            path.unlink()

    lines = [
        "Hearth Lane work agent — draft then confirm",
        "model=scripted (no model server on this path)",
        "principal=counter-staff",
        f"from={FROM_ADDRESS}",
        "smtp=not_used",
        "",
    ]

    read_decision = decide("read_file", {"path": "policy.md"})
    observed = read_file(DOCS, "policy.md")
    first = observed.splitlines()[0] if observed else "(empty)"
    lines.append("[1] read_file")
    lines.append("    " + format_decision(read_decision).replace("\n", "\n    "))
    lines.append(f"    result={first}")
    lines.append("")

    problem = policy_ready()
    if problem:
        lines.append("[2] draft_email")
        lines.append(f"    result={problem}")
        lines.append("--- summary ---")
        lines.append("drafts=0 sent=0")
        return "\n".join(lines) + "\n"

    draft = build_draft()
    draft_decision = decide(
        "draft_email",
        {"to": draft["to"], "subject": draft["subject"]},
    )
    drafts_dir.mkdir(parents=True, exist_ok=True)
    draft_path = drafts_dir / f"{draft['draft_id']}.json"
    draft_path.write_text(json.dumps(draft, indent=2) + "\n", encoding="utf-8")
    lines.append("[2] draft_email")
    lines.append("    " + format_decision(draft_decision).replace("\n", "\n    "))
    lines.append(f"    result=draft written {draft_path.name} status=draft")
    lines.append("    draft_body:")
    for body_line in draft["body"].splitlines():
        lines.append(f"    | {body_line}")
    lines.append("")

    payload = send_arguments(draft)
    send_decision = decide(
        "send_draft",
        payload,
        confirmed_token=confirmed_token,
        allow_external_mail=True,
    )
    lines.append("[3] send_draft")
    lines.append("    " + format_decision(send_decision).replace("\n", "\n    "))
    if send_decision["decision"] == "allowed" and send_decision["confirmed"]:
        sent = {
            **draft,
            "status": "sent",
            "acted_as": "counter-staff",
            "confirmed_by": "operator",
            "transport": "local-outbox",
            "smtp": "not_used",
        }
        sent_dir.mkdir(parents=True, exist_ok=True)
        sent_path = sent_dir / f"{draft['draft_id']}.json"
        sent_path.write_text(json.dumps(sent, indent=2) + "\n", encoding="utf-8")
        lines.append(f"    result=sent locally {sent_path.name} confirmed_by=operator")
    else:
        lines.append("    result=not sent; outbox unchanged")
    lines.append("")

    draft_count = len(list(drafts_dir.glob("*.json"))) if drafts_dir.exists() else 0
    sent_count = len(list(sent_dir.glob("*.json"))) if sent_dir.exists() else 0
    lines.append("--- summary ---")
    lines.append(f"drafts={draft_count} sent={sent_count}")
    if send_decision["decision"] != "allowed":
        lines.append(
            "To send this exact draft, rerun with:\n"
            "  python labs/ch17-work-agent-blueprint/draft_mail.py "
            f"--confirm {send_decision['approval_token']}"
        )
    lines.append(
        "The From address stays counter@hearthlane.example. "
        "A token for a different body does not send this draft."
    )
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

    policy = (DOCS / "policy.md").read_text(encoding="utf-8")
    for sentence in POLICY_SENTENCES:
        expect(sentence in policy, "policy still contains a quoted sentence")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        drafts = root / "drafts"
        sent = root / "sent"
        pending = run_mail(None, drafts, sent)
        expect("status=draft" in pending, "draft is written without a token")
        expect("sent=0" in pending, "send waits")
        expect("smtp=not_used" in pending, "no smtp")
        expect(not any(sent.glob("*.json")), "sent directory stays empty")

        draft = build_draft()
        token = approval_token("send_draft", send_arguments(draft))
        approved = run_mail(token, drafts, sent)
        expect("sent=1" in approved, "matching token sends")
        expect("confirmed_by=operator" in approved, "operator is recorded")
        sent_files = list(sent.glob("*.json"))
        expect(len(sent_files) == 1, "one sent file")
        payload = json.loads(sent_files[0].read_text(encoding="utf-8"))
        expect(payload["from"] == FROM_ADDRESS, "from address is the counter")
        expect(payload["acted_as"] == "counter-staff", "acted_as is counter staff")
        expect(payload["smtp"] == "not_used", "sent record did not use smtp")

        stale = dict(send_arguments(draft))
        stale["body"] = stale["body"] + "\nPlease refund cash."
        moved = run_mail(approval_token("send_draft", stale), drafts, sent)
        expect("sent=0" in moved, "a token for a different body does not send")

        # Chapter 16's concierge flag: the same external address is never.
        concierge = decide("send_draft", send_arguments(draft), confirmed_token=token)
        expect(concierge["decision"] == "denied", "concierge still never-sends externally")

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
    if args.reset:
        for folder in (DRAFTS, SENT):
            if folder.exists():
                for path in folder.glob("*.json"):
                    path.unlink()
    print(run_mail(args.confirm, DRAFTS, SENT), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
