#!/usr/bin/env python3
# pylint:disable=missing-class-docstring,missing-function-docstring,missing-module-docstring

import argparse
import csv
from dataclasses import dataclass
from typing import Literal


Direction = Literal["income", "expense", "transfer"]


@dataclass(frozen=True, kw_only=True, slots=True)
class Transaction:
    date: str
    direction: Direction
    src: str
    dest: str
    amount: float
    note: str


ONEMONEY_DATE_HEADERS = ["ДАТА"]
ONEMONEY_DIRECTION_HEADERS = ["ТИП"]
ONEMONEY_DIRECTION_MAP: dict[str, Direction] = {
    "Доход": "income",
    "Расход": "expense",
    "Перевод": "transfer",
}
ONEMONEY_SRC_HEADERS = ["СО СЧЁТА"]
ONEMONEY_DEST_HEADERS = ["НА СЧЁТ/НА КАТЕГОРИЮ"]
ONEMONEY_AMOUNT_HEADERS = ["СУММА"]
ONEMONEY_NOTE_HEADERS = ["ЗАМЕТКИ"]


def get_onemoney_header(candidates: list[str], row: dict[str, str]) -> str:
    for candidate in candidates:
        if candidate in row:
            return row[candidate]
    raise ValueError(
        f"No header matching {', '.join(candidates)} found. Headers: {', '.join(row.keys())}"
    )


def get_onemoney_direction(row: dict[str, str]) -> Direction:
    direction_str = get_onemoney_header(ONEMONEY_DIRECTION_HEADERS, row)
    try:
        return ONEMONEY_DIRECTION_MAP[direction_str]
    except KeyError as e:
        raise ValueError(f"Unknown direction: {direction_str} (data: {row!r})") from e


def read_1money_csv(onemoney_file) -> list[Transaction]:
    reader = csv.DictReader(onemoney_file, quoting=csv.QUOTE_ALL)
    transactions = []
    for row in reader:
        if all(value == "" or value == None for value in row.values()):
            break
        transactions.append(
            Transaction(
                date=get_onemoney_header(ONEMONEY_DATE_HEADERS, row),
                direction=get_onemoney_direction(row),
                src=get_onemoney_header(ONEMONEY_SRC_HEADERS, row),
                dest=get_onemoney_header(ONEMONEY_DEST_HEADERS, row),
                amount=float(get_onemoney_header(ONEMONEY_AMOUNT_HEADERS, row)),
                note=get_onemoney_header(ONEMONEY_NOTE_HEADERS, row),
            )
        )
    return transactions


def write_cashew_csv(cashew_file, transactions: list[Transaction]) -> None:
    writer = csv.DictWriter(
        cashew_file,
        fieldnames=["date", "amount", "category name", "title", "note", "account"],
    )
    writer.writeheader()

    for transaction in transactions:
        out = {
            "date": transaction.date,
            "category name": transaction.dest,
            "title": "",
            "note": transaction.note,
            "account": transaction.src,
        }

        if transaction.direction == 'transfer':
            out["category name"] = "Balance Correction"
            out["note"] = f"Balance transfer\n{transaction.src} -> {transaction.dest}"
            # from
            writer.writerow({**out, "amount": -transaction.amount})
            # to
            writer.writerow({**out, "account": transaction.dest, "amount": transaction.amount})
        elif transaction.direction == 'income':
            writer.writerow({**out, "amount": transaction.amount})
        elif transaction.direction == 'expense':
            writer.writerow({**out, "amount": -transaction.amount})
        else:
            raise ValueError(f"Unknown direction: {transaction.direction}")


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

    transactions = read_1money_csv(input_file)
    print(f"Imported {len(transactions)} transactions.")

    write_cashew_csv(output_file, transactions)


if __name__ == "__main__":
    main()
