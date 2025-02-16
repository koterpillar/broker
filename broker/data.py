from collections.abc import Iterable
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
