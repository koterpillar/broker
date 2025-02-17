import csv

from .data import Transaction, row_date


def read_bank_csv(bank_file) -> list[Transaction]:
    reader = csv.DictReader(bank_file)
    transactions = []
    account = "Bank"
    for row in reader:
        dt = row_date(row)

        if row["Debit"]:
            amount = -float(row["Debit"])
            transactions.append(
                Transaction(
                    date=dt,
                    direction="expense",
                    src=account,
                    dest=row["Narration"],
                    amount=amount,
                    note="",
                )
            )
        elif row["Credit"]:
            amount = float(row["Credit"])
            transactions.append(
                Transaction(
                    date=dt,
                    direction="income",
                    src=row["Narration"],
                    dest=account,
                    amount=amount,
                    note="",
                )
            )
        else:
            raise ValueError(f"Neither Debit nor Credit found in {row!r}")
    return transactions
