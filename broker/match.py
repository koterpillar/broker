import argparse
from dataclasses import dataclass
from typing import Optional

import yaml

from .bank import read_bank_csv
from .cashew import read_cashew_csv
from .data import Transaction


@dataclass(frozen=True, kw_only=True, slots=True)
class Hint:
    bank: str
    cashew: str


def read_hints(hints_file) -> list[Hint]:
    contents = yaml.safe_load(hints_file)
    return [Hint(**row) for row in contents]


UNMATCHED_TXN_SCORE = 1000


def matches(txn: Transaction, bank_txn: Transaction, hints: list[Hint]) -> Optional[int]:
    if txn.amount != bank_txn.amount:
        return False
    if txn.direction != bank_txn.direction:
        return False
    score = 0
    days_diff = abs(txn.date - bank_txn.date).days
    if days_diff > 5:
        return False
    score += days_diff * 10
    if not any(hint.bank == bank_txn.note and hint.cashew == txn.dest for hint in hints):
        score += 500
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Match Cashew transactions to bank")
    parser.add_argument(
        "cashew_file", type=argparse.FileType("r"), help="Cashew CSV file"
    )
    parser.add_argument("bank_file", type=argparse.FileType("r"), help="Bank CSV file")
    parser.add_argument("-a", "--account", help="Account name")
    parser.add_argument("--hints", type=argparse.FileType("r"), help="Match hints")
    args = parser.parse_args()

    cashew_file = args.cashew_file
    bank_file = args.bank_file

    all_transactions = read_cashew_csv(cashew_file)
    transactions = [t for t in all_transactions if args.account in t.accounts]
    min_date = min(t.date for t in transactions)
    max_date = max(t.date for t in transactions)
    for txn in transactions:
        if txn.amount < 0:
            raise ValueError(f"Negative amount {txn.amount} in {txn}.")
    print(
        f"Imported {len(transactions)} Cashew transactions from {min_date} to {max_date}."
    )

    all_bank_transactions = read_bank_csv(bank_file)
    bank_transactions = [
        t for t in all_bank_transactions if min_date <= t.date <= max_date
    ]
    print(f"Imported {len(bank_transactions)} bank transactions.")

    hints = read_hints(args.hints) if args.hints else []

    matched = set()

    for bank_txn in bank_transactions:
        candidates = []
        for txn in transactions:
            if txn in matched:
                continue
            if score := matches(txn, bank_txn, hints):
                candidates.append((score, txn))

        if not candidates:
            print(f"Could not match {bank_txn}")
            continue

        if len(candidates) > 1:
            print(f"Multiple candidates for {bank_txn}:")
            for score, candidate in candidates:
                print(score, candidate)

        _, txn = candidates[0]
        matched.add(txn)
        # FIXME: backtracking
