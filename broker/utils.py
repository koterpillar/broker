def words(*parts: str) -> str:
    return " ".join(part for part in parts if part)
