import csv
import re

from .data import Row, Transaction, row_value

DATE_COLUMNS = ["Transaction Date"]


def bank_date(row: Row) -> str:
    # FIXME: dates are strings
    result = row_value(DATE_COLUMNS, row)
    if match := re.match(r"^(\d{2})/(\d{2})/(\d{4})$", result):
        # Convert DD/MM/YYYY to YYYY-MM-DD
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    return result


def read_bank_csv(bank_file) -> list[Transaction]:
    reader = csv.DictReader(bank_file)
    transactions = []
    account = "Bank"
    for row in reader:
        dt = bank_date(row)

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
