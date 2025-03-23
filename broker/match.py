import argparse
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Optional

import yaml

from .astar import AStar
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


Matching = tuple[frozenset[Transaction], frozenset[Transaction]]


class MatchAStar(AStar[Matching]):
    def __init__(self, hints: list[Hint]):
        self.hints = hints
        self.give_up = False

    def is_goal(self, node: Matching) -> bool:
        txns, bank_txns = node
        return not txns and not bank_txns

    def heuristic(self, node: Matching) -> float:
        txns, bank_txns = node
        return (len(txns) + len(bank_txns)) * 1000

    def matches(self, txn: Transaction, bank_txn: Transaction) -> Optional[int]:
        if txn.amount != bank_txn.amount:
            return False
        if txn.direction != bank_txn.direction:
            return False
        score = 0
        days_diff = abs(txn.date - bank_txn.date).days
        if days_diff > 5:
            return False
        score += days_diff * 10
        if not any(
            bank_txn.note.startswith(hint.bank) and hint.cashew == txn.dest
            for hint in self.hints
        ):
            score += 500
        return score

    give_up: bool

    def get_neighbors(self, node: Matching) -> Iterator[tuple[Matching, float]]:
        if self.give_up:
            return

        txns, bank_txns = node
        print(
            f"Matching between {len(txns)} Cashew and {len(bank_txns)} bank transactions."
        )
        if len(txns) + len(bank_txns) <= 105:
            # give up
            print("Giving up.")
            self.give_up = True
            return

        for txn in txns:
            for bank_txn in bank_txns:
                if score := self.matches(txn, bank_txn):
                    new_node = (txns - {txn}, bank_txns - {bank_txn})
                    yield (new_node, score)

    def run(
        self, transactions: list[Transaction], bank_transactions: list[Transaction]
    ):
        start = (frozenset(transactions), frozenset(bank_transactions))
        return self.search(start)


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

    matcher = MatchAStar(hints)

    matches = matcher.run(transactions, bank_transactions)
    print(matches)
