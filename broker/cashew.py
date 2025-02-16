import csv
from collections.abc import Iterable

from .data import Transaction


def cashew_rows(transaction: Transaction) -> Iterable[dict[str, str | float]]:
    out = {
        "date": transaction.date,
        "category name": transaction.dest,
        "title": "",
        "note": transaction.note,
        "account": transaction.src,
    }

    if transaction.direction == "transfer":
        out["category name"] = "Balance Correction"
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
