#!/usr/bin/env python3
# pylint:disable=missing-class-docstring,missing-function-docstring,missing-module-docstring

import argparse
import csv
from dataclasses import dataclass
from typing import Literal


Direction = Literal["income", "expense", "transfer"]


@dataclass
class Transaction:
    date: str
    direction: Direction
    src: str
    dest: str
    amount: float


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
        date = get_onemoney_header(ONEMONEY_DATE_HEADERS, row)
        direction = get_onemoney_direction(row)
        src = get_onemoney_header(ONEMONEY_SRC_HEADERS, row)
        dest = get_onemoney_header(ONEMONEY_DEST_HEADERS, row)
        amount = float(get_onemoney_header(ONEMONEY_AMOUNT_HEADERS, row))
        transactions.append(Transaction(date, direction, src, dest, amount))
    return transactions


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert 1Money CSV to Cashew")
    parser.add_argument(
        "input_file", type=argparse.FileType("r", encoding="utf-8-sig"), help="1Money CSV file"
    )
    parser.add_argument(
        "output_file", type=argparse.FileType("w"), help="Cashew import file"
    )
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    transactions = read_1money_csv(input_file)
    print(f"Imported {len(transactions)} transactions.")


if __name__ == "__main__":
    main()
