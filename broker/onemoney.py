import csv

from .data import Direction, Transaction

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


def read_onemoney_csv(onemoney_file) -> list[Transaction]:
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
