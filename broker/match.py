import argparse
from datetime import timedelta

from .bank import read_bank_csv
from .cashew import read_cashew_csv
from .data import Transaction


def matches(txn: Transaction, bank_txn: Transaction) -> bool:
    if txn.amount != bank_txn.amount:
        return False
    if txn.direction != bank_txn.direction:
        return False
    date_delta = abs(txn.date - bank_txn.date)
    if date_delta < timedelta(days=-2):
        return False
    if date_delta > timedelta(days=2):
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Match Cashew transactions to bank")
    parser.add_argument(
        "cashew_file", type=argparse.FileType("r"), help="Cashew CSV file"
    )
    parser.add_argument("bank_file", type=argparse.FileType("r"), help="Bank CSV file")
    parser.add_argument("-a", "--account", help="Account name")
    args = parser.parse_args()

    cashew_file = args.cashew_file
    bank_file = args.bank_file

    all_transactions = read_cashew_csv(cashew_file)
    transactions = [t for t in all_transactions if args.account in t.accounts]
    min_date = min(t.date for t in transactions)
    max_date = max(t.date for t in transactions)
    print(
        f"Imported {len(transactions)} Cashew transactions from {min_date} to {max_date}."
    )

    for txn in transactions:
        if txn.amount < 0:
            print(txn.amount)
            print(txn)
            raise ValueError("Negative amount")

    all_bank_transactions = read_bank_csv(bank_file)
    bank_transactions = [
        t for t in all_bank_transactions if min_date <= t.date <= max_date
    ]
    print(f"Imported {len(bank_transactions)} bank transactions.")

    for bank_txn in bank_transactions:
        candidates = [t for t in transactions if matches(t, bank_txn)]
        if len(candidates) == 1:
            # FIXME: remove matched transaction
            # FIXME: backtracking
            continue
        if len(candidates) > 1:
            print(f"Multiple candidates for {bank_txn}:")
            for candidate in candidates:
                print(candidate)
            raise ValueError("Multiple candidates")
        print(f"Could not match {bank_txn}")
