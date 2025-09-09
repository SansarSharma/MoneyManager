# File: models/transaction.py

from __future__ import annotations
from dataclasses import dataclass

"""
Represents a single financial entry read/written to the workbook.

Abstraction Function:
- A Transaction is a record with (date, day, category, amount, type, description).
- It corresponds to one row in the Excel month/day grid.

Representation Invariant:
- date is a string "YYYY-MM-DD" (may be empty during edits)
- day is a short weekday label from the sheet (e.g., "Mon") or ""
- category is an UPPERCASE non-empty string when present
- amount >= 0 (coerced to float defensively)
- type ∈ {"INCOME", "EXPENSE"}  (legacy rows may be normalized)
- description is free text ("" allowed)
"""


@dataclass
class Transaction:
    # Canonical shape (explicit types, Java-style clarity)
    date: str
    day: str
    category: str
    amount: float
    type: str   # "INCOME" or "EXPENSE"
    description: str

    def __post_init__(self) -> None:
        """
        REQUIRES: fields may be loosely formatted from I/O
        MODIFIES: self
        EFFECTS:  Normalizes strings, uppercases category/type, and coerces amount to float.
        """
        self.date = (self.date or "").strip()
        self.day = (self.day or "").strip()
        self.category = (self.category or "").strip().upper()
        self.description = (self.description or "").strip()
        self.type = (self.type or "").strip().upper()
        try:
            self.amount = float(self.amount)
        except (TypeError, ValueError):
            self.amount = 0.0

    # ------------------------------------------------------------------
    # Legacy compatibility layer (kept to avoid breaking older callers)
    # ------------------------------------------------------------------

    # ----- GETTERS (legacy names) -----
    def get_amount(self) -> float:
        """EFFECTS: Returns the amount."""
        return self.amount

    def get_category(self) -> str:
        """EFFECTS: Returns the category."""
        return self.category

    def get_type(self) -> str:
        """EFFECTS: Returns the type (INCOME/EXPENSE)."""
        return self.type

    def get_description(self) -> str:
        """EFFECTS: Returns the description."""
        return self.description

    # The old model exposed year/month/day separately; we map them from date.
    def get_year(self) -> str:
        """EFFECTS: Returns YYYY (string) if available, else ""."""
        return self.date.split("-")[0] if self.date and "-" in self.date else ""

    def get_month(self) -> str:
        """EFFECTS: Returns MM (string, zero-padded) if available, else ""."""
        parts = self.date.split("-")
        return parts[1] if len(parts) >= 2 else ""

    def get_day(self) -> int:
        """EFFECTS: Returns DD (int) if available, else 0."""
        try:
            return int(self.date.split("-")[2])
        except Exception:
            return 0

    # ----- SETTERS (legacy names) -----
    def set_amount(self, new_amount: float) -> None:
        """
        REQUIRES: new_amount is numeric
        MODIFIES: self
        EFFECTS:  Sets amount; invalid input coerces to 0.0.
        """
        try:
            self.amount = float(new_amount)
        except (TypeError, ValueError):
            self.amount = 0.0

    def set_category(self, new_category: str) -> None:
        """
        REQUIRES: new_category may be any string
        MODIFIES: self
        EFFECTS:  Sets category (uppercased, trimmed).
        """
        self.category = (new_category or "").strip().upper()

    def set_type(self, new_type: str) -> None:
        """
        REQUIRES: new_type ∈ {"INCOME","EXPENSE"} (validated elsewhere)
        MODIFIES: self
        EFFECTS:  Sets type (uppercased, trimmed).
        """
        self.type = (new_type or "").strip().upper()

    def set_description(self, new_description: str) -> None:
        """
        REQUIRES: any string
        MODIFIES: self
        EFFECTS:  Sets description (trimmed).
        """
        self.description = (new_description or "").strip()

    def set_year(self, new_year: str) -> None:
        """
        REQUIRES: new_year is "YYYY" or empty
        MODIFIES: self
        EFFECTS:  Rewrites date preserving MM-DD if present.
        """
        yy: str = (new_year or "").strip()
        parts = (self.date or "").split("-")
        mm: str = parts[1] if len(parts) >= 2 else "01"
        dd: str = parts[2] if len(parts) >= 3 else "01"
        if yy:
            self.date = f"{yy}-{mm}-{dd}"

    def set_month(self, new_month: str) -> None:
        """
        REQUIRES: new_month like "3" or "03"
        MODIFIES: self
        EFFECTS:  Rewrites date preserving YYYY and DD.
        """
        mm_raw: str = (new_month or "").strip()
        try:
            mm_i: int = int(mm_raw)
        except Exception:
            mm_i = 1
        mm: str = f"{mm_i:02d}"
        parts = (self.date or "").split("-")
        yy: str = parts[0] if len(parts) >= 1 and parts[0] else "0000"
        dd: str = parts[2] if len(parts) >= 3 else "01"
        self.date = f"{yy}-{mm}-{dd}"

    def set_day(self, new_day: int) -> None:
        """
        REQUIRES: 1 <= new_day <= 31
        MODIFIES: self
        EFFECTS:  Rewrites date preserving YYYY and MM.
        """
        try:
            dd_i: int = int(new_day)
        except Exception:
            dd_i = 1
        dd: str = f"{dd_i:02d}"
        parts = (self.date or "").split("-")
        yy: str = parts[0] if len(parts) >= 1 and parts[0] else "0000"
        mm: str = parts[1] if len(parts) >= 2 else "01"
        self.date = f"{yy}-{mm}-{dd}"
