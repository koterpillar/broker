import argparse

from .cashew import write_cashew_csv
from .data import Transaction
from .onemoney import read_onemoney_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert 1Money CSV to Cashew")
    parser.add_argument(
        "input_file",
        type=argparse.FileType("r", encoding="utf-8-sig"),
        help="1Money CSV file",
    )
    parser.add_argument(
        "output_file", type=argparse.FileType("w"), help="Cashew import file"
    )
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    transactions = read_onemoney_csv(input_file)
    print(f"Imported {len(transactions)} transactions.")

    write_cashew_csv(output_file, transactions)

    for acct, balance in Transaction.balances(transactions).items():
        print(f"Final balance for {acct}: {balance}")
