import argparse

from .cashew import read_cashew_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Match Cashew transactions to bank")
    parser.add_argument(
        "input_file", type=argparse.FileType("r"), help="Cashew CSV file"
    )
    parser.add_argument("-a", "--account", help="Account name")
    args = parser.parse_args()

    input_file = args.input_file

    all_transactions = read_cashew_csv(input_file)
    transactions = [t for t in all_transactions if args.account in t.accounts]
    print(f"Imported {len(transactions)} transactions.")
