import argparse

from .bank import read_bank_csv
from .cashew import read_cashew_csv


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
    print(f"Imported {len(transactions)} Cashew transactions.")

    bank_transactions = read_bank_csv(bank_file)
    print(f"Imported {len(bank_transactions)} bank transactions.")
