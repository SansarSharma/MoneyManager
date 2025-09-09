# File: models/user_profile.py

from typing import Dict, List
from models.transaction import Transaction

"""
Represents a user's financial profile (income + day-based transactions).

Abstraction Function:
- Stores current income and a mapping of date → list of Transaction.

Representation Invariant:
- _current_income >= 0
- _transactions: Dict["YYYY-MM-DD", List[Transaction]]
"""


class UserProfile:
    def __init__(self, current_income: float = 0.0):
        """
        REQUIRES: current_income >= 0
        MODIFIES: self
        EFFECTS:  Initializes the profile with income and an empty transactions dict.
        """
        self._current_income: float = current_income
        self._transactions: Dict[str, List[Transaction]] = {}  # Key: "YYYY-MM-DD"

    # ---------------- Income ----------------

    def get_current_income(self) -> float:
        """
        REQUIRES: nothing
        MODIFIES: nothing
        EFFECTS:  Returns the current income.
        """
        return self._current_income

    def set_current_income(self, new_income: float) -> None:
        """
        REQUIRES: new_income >= 0
        MODIFIES: self
        EFFECTS:  Updates the user's current income.
        """
        self._current_income = new_income

    # ---------------- Transactions ----------------

    def get_transactions(self) -> Dict[str, List[Transaction]]:
        """
        REQUIRES: nothing
        MODIFIES: nothing
        EFFECTS:  Returns the internal transaction dictionary.
        """
        return self._transactions

    def set_transactions(self, transactions: Dict[str, List[Transaction]]) -> None:
        """
        REQUIRES: transactions is Dict[str, List[Transaction]]
        MODIFIES: self
        EFFECTS:  Replaces the internal transaction dictionary.
        """
        self._transactions = transactions
