"""Exact salary arithmetic; never use binary floats for compensation."""
import re
from decimal import Decimal

SALARY_PATTERN = re.compile(r"^(?:[0-9]{1,12})(?:\.[0-9]{1,2})?$")
MAX_MINOR_UNITS = 99_999_999_999_999


def parse_salary(value: str) -> int:
    if not isinstance(value, str) or not SALARY_PATTERN.fullmatch(value):
        raise ValueError("Enter a positive salary with at most two decimal places")
    amount = int(Decimal(value) * 100)
    if not 0 < amount <= MAX_MINOR_UNITS:
        raise ValueError("Salary must be greater than zero and within allowed bounds")
    return amount


def format_salary(minor: int) -> str:
    return f"{minor // 100}.{minor % 100:02d}"
