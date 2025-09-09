# File: models/financial_summary.py

from __future__ import annotations
from typing import Optional


class FinancialSummary:
    """
    REQUIRES: valid numeric values for amounts and year; strings must not be None.
    MODIFIES: none
    EFFECTS:  Represents a snapshot of financial results for a given year.

    Abstraction Function:
        AF(self) = A yearly snapshot of finances where
                   total_income = self._total_income,
                   total_expense = self._total_expense,
                   net_savings = self._net_savings,
                   year = self._year,
                   notes = self._notes

    Representation Invariant:
        - self._year >= 0
        - self._total_income >= 0
        - self._total_expense >= 0
        - self._net_savings = self._total_income - self._total_expense
    """

    def __init__(self, year: int, total_income: float, total_expense: float,
                 net_savings: float, notes: Optional[str] = None) -> None:
        """
        REQUIRES: year >= 0; total_income >= 0; total_expense >= 0
        MODIFIES: self
        EFFECTS:  Initializes a FinancialSummary with the given values.
        """
        self._year: int = year
        self._total_income: float = total_income
        self._total_expense: float = total_expense
        self._net_savings: float = net_savings
        self._notes: Optional[str] = notes

    # Getters
    def get_year(self) -> int:
        """EFFECTS: Returns the year of this summary."""
        return self._year

    def get_total_income(self) -> float:
        """EFFECTS: Returns the total income."""
        return self._total_income

    def get_total_expense(self) -> float:
        """EFFECTS: Returns the total expenses."""
        return self._total_expense

    def get_net_savings(self) -> float:
        """EFFECTS: Returns the net savings (income - expenses)."""
        return self._net_savings

    def get_notes(self) -> Optional[str]:
        """EFFECTS: Returns the optional notes string, or None if not set."""
        return self._notes

    # Setters
    def set_year(self, year: int) -> None:
        """MODIFIES: self; EFFECTS: Updates the year."""
        self._year = year

    def set_total_income(self, income: float) -> None:
        """MODIFIES: self; EFFECTS: Updates the total income."""
        self._total_income = income

    def set_total_expense(self, expense: float) -> None:
        """MODIFIES: self; EFFECTS: Updates the total expenses."""
        self._total_expense = expense

    def set_net_savings(self, savings: float) -> None:
        """MODIFIES: self; EFFECTS: Updates the net savings."""
        self._net_savings = savings

    def set_notes(self, notes: Optional[str]) -> None:
        """MODIFIES: self; EFFECTS: Updates the notes."""
        self._notes = notes
