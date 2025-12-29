import re


AMOUNT_RE = re.compile(r"([\d,]+\.\d{2})")


def parse_amount(value: str) -> float:
    return float(value.replace(",", ""))


def is_transaction_line(line: str) -> bool:
    # Starts with date like 02/05/25
    return bool(re.match(r"\d{2}/\d{2}/\d{2}", line))
