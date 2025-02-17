import csv
from collections.abc import Iterable

from .data import Direction, Row, Transaction, row_date
from .utils import words

BALANCE_CORRECTION = ["Balance Correction", "Коррекция баланса"]


def cashew_rows(transaction: Transaction) -> Iterable[dict[str, str | float]]:
    out = {
        "date": transaction.date.strftime("%Y-%m-%d"),
        "category name": transaction.dest,
        "title": "",
        "note": transaction.note,
        "account": transaction.src,
    }

    if transaction.direction == "transfer":
        out["category name"] = BALANCE_CORRECTION[0]
        out["note"] = f"Balance transfer: {transaction.src} -> {transaction.dest}"
        # from
        yield {**out, "amount": -transaction.amount}
        # to
        yield {**out, "account": transaction.dest, "amount": transaction.amount}
    elif transaction.direction == "income":
        yield {**out, "amount": transaction.amount}
    elif transaction.direction == "expense":
        yield {**out, "amount": -transaction.amount}
    else:
        raise ValueError(f"Unknown direction: {transaction.direction}")


def write_cashew_csv(cashew_file, transactions: Iterable[Transaction]) -> None:
    writer = csv.DictWriter(
        cashew_file,
        fieldnames=["date", "amount", "category name", "title", "note", "account"],
    )
    writer.writeheader()

    for transaction in transactions:
        for row in cashew_rows(transaction):
            writer.writerow(row)


def cashew_direction(row: Row) -> Direction:
    if row["category name"] in BALANCE_CORRECTION:
        return "transfer"
    if row["income"] == "true":
        return "income"
    return "expense"


def read_cashew_csv(cashew_file) -> list[Transaction]:
    reader = csv.DictReader(cashew_file)
    transactions = []
    for row in reader:
        if row["category name"] in BALANCE_CORRECTION:
            # FIXME process transfers
            continue

        transactions.append(
            Transaction(
                date=row_date(row),
                direction=cashew_direction(row),
                src=row["account"],
                dest=words(row["category name"], row["subcategory name"]),
                amount=abs(float(row["amount"])),
                note=words(row["title"], row["note"]),
            )
        )
    return transactions
