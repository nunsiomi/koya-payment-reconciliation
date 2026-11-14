#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json


def parse_amount(value):
    """Amounts come as numbers or as strings like "4,804.15"."""
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return float(value)


# Keep only the latest attempt (highest ts) for each txn_id.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # unreadable line
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if not txn_id:
            continue  # no txn_id

        current = latest.get(txn_id)
        # ts is always "YYYY-MM-DDTHH:MM:SSZ", so string comparison is time order.
        if current is None or event["ts"] > current["ts"]:
            latest[txn_id] = event

total = 0.0
count = 0
for event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
