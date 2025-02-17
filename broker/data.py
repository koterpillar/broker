import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

Direction = Literal["income", "expense", "transfer"]


@dataclass(frozen=True, kw_only=True, slots=True)
class Transaction:
    date: datetime
    direction: Direction
    src: str
    dest: str
    amount: float
    note: str

    @property
    def accounts(self) -> Iterable[str]:
        yield self.src
        if self.direction == "transfer":
            yield self.dest

    @staticmethod
    def balances(transactions: Iterable["Transaction"]) -> dict[str, float]:

        accounts = set(a for transaction in transactions for a in transaction.accounts)
        balance = {a: 0.0 for a in accounts}

        for transaction in transactions:
            if transaction.direction == "income":
                balance[transaction.src] += transaction.amount
            elif transaction.direction == "expense":
                balance[transaction.src] -= transaction.amount
            elif transaction.direction == "transfer":
                balance[transaction.src] -= transaction.amount
                balance[transaction.dest] += transaction.amount
            else:
                raise ValueError(
                    f"Unknown direction: {transaction.direction} for {transaction!r}"
                )

        for account in balance:
            balance[account] = round(balance[account], 4)

        return balance


Row = dict[str, str]


def row_value(candidates: list[str], row: Row) -> str:
    for candidate in candidates:
        if candidate in row:
            return row[candidate]
    raise ValueError(
        f"No header matching {', '.join(candidates)} found. Headers: {', '.join(row.keys())}"
    )


DATE_COLUMNS = ["date", "Transaction Date", "ДАТА"]


def row_date(row: Row) -> datetime:
    result = row_value(DATE_COLUMNS, row)
    if match := re.match(r"^(\d{2})[./](\d{2})[./](\d{4})$", result):
        # Convert DD/MM/YYYY to YYYY-MM-DD
        return datetime(
            year=int(match.group(3)), month=int(match.group(2)), day=int(match.group(1))
        )
    if match := re.match(
        r"^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}).000$", result
    ):
        return datetime(
            year=int(match.group(1)),
            month=int(match.group(2)),
            day=int(match.group(3)),
            hour=int(match.group(4)),
            minute=int(match.group(5)),
            second=int(match.group(6)),
        )
    raise ValueError(f"Invalid date format: {result}")
