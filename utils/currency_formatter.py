# File: utils/currency_formatter.py
"""
Very small helper for displaying money consistently.

- Accepts int or float (non-negative expected).
- Returns a string with a dollar sign and commas.
- If the value has cents, shows 2 decimals; otherwise no decimals.
"""

from typing import Union

Number = Union[int, float]


def format_currency(amount: Number) -> str:
    """
    REQUIRES: amount >= 0 (app logic ensures non-negative)
    EFFECTS: Returns "$1,234" for whole numbers, "$1,234.56" if cents exist.
    """
    try:
        val = float(amount)
    except (TypeError, ValueError):
        val = 0.0

    if val < 0:
        # App design uses only non-negative amounts; guard anyway.
        val = 0.0

    # Show decimals only when needed
    if abs(val - int(val)) < 1e-9:
        return f"${int(val):,}"
    return f"${val:,.2f}"


class CurrencyFormatter:
    """
    Simple wrapper class in case you prefer OO calls:
        CurrencyFormatter.format(1234) -> "$1,234"
    """

    @staticmethod
    def format(amount: Number) -> str:
        return format_currency(amount)
