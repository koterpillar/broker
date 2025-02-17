import csv
import re

from .data import Row, Transaction, row_date, row_value

NOTE_COLUMNS = ["Narration"]


def bank_note(row: Row) -> str:
    value = row_value(NOTE_COLUMNS, row)
    value = re.sub(r" *([A-Z])  ([A-Za-z ]{12})  ([A-Z]{2})$", r" \1\2 \3", value)
    return value


def read_bank_csv(bank_file) -> list[Transaction]:
    reader = csv.DictReader(bank_file)
    transactions = []
    account = "Bank"
    for row in reader:
        dt = row_date(row)
        note = bank_note(row)

        if row["Debit"]:
            amount = float(row["Debit"])
            transactions.append(
                Transaction(
                    date=dt,
                    direction="expense",
                    src=account,
                    dest=note,
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
                    src=note,
                    dest=account,
                    amount=amount,
                    note="",
                )
            )
        else:
            raise ValueError(f"Neither Debit nor Credit found in {row!r}")
    return transactions
