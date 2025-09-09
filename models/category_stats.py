# File: models/category_stats.py
#
# CategoryStats groups transactions by category.

from typing import Dict, List
from models.transaction import Transaction

"""
Abstraction Function:
- Maintains category → List[Transaction] for supported categories.
- Expense categories + two special buckets (INCOME, NONE).

Representation Invariant:
- _categories contains every supported key.
- Unknown categories are routed to MISCELLANEOUS.
"""

# ----------------------------- Supported Categories -----------------------------

EXPENSE_CATEGORIES: List[str] = [
    "HOUSING",
    "TRANSPORTATION",
    "INSURANCE",
    "SCHOOL",
    "FOOD",
    "PERSONAL CARE",
    "SUBSCRIPTIONS",
    "HOLIDAY EXPENSES",
    "MISCELLANEOUS",
]

SPECIAL_CATEGORIES: List[str] = [
    "INCOME",   # special bucket for income rows
    "NONE",     # special bucket for explicitly empty days/rows
]

ALL_CATEGORIES: List[str] = EXPENSE_CATEGORIES + SPECIAL_CATEGORIES


class CategoryStats:
    """
    Minimal data model for storing transactions by category.
    No analytics or file I/O here—just list management.
    """

    def __init__(self) -> None:
        """
        REQUIRES: nothing
        MODIFIES: self
        EFFECTS: Initializes empty lists for every supported category.
        """
        self._categories: Dict[str, List[Transaction]] = {c: [] for c in ALL_CATEGORIES}

    # ----------------------------- Add / Get / Set -----------------------------

    def add_transaction(self, category: str, transaction: Transaction) -> None:
        """
        REQUIRES: transaction is a valid Transaction
        MODIFIES: self
        EFFECTS:  Appends to category (unknown → MISCELLANEOUS).
        """
        key: str = (category or "").strip().upper()
        if key not in self._categories:
            key = "MISCELLANEOUS"
        self._categories[key].append(transaction)

    def get_transactions(self, category: str) -> List[Transaction]:
        """
        REQUIRES: category is a string
        MODIFIES: nothing
        EFFECTS:  Returns a shallow copy of the list for the category
                  (unknown → MISCELLANEOUS).
        """
        key: str = (category or "").strip().upper()
        if key not in self._categories:
            key = "MISCELLANEOUS"
        return list(self._categories[key])

    def set_transactions(self, category: str, transactions: List[Transaction]) -> None:
        """
        REQUIRES: transactions is List[Transaction]
        MODIFIES: self
        EFFECTS:  Replaces the list for the category (unknown → MISCELLANEOUS).
        """
        key: str = (category or "").strip().upper()
        if key not in self._categories:
            key = "MISCELLANEOUS"
        self._categories[key] = list(transactions)

    # ----------------------------- Bulk Accessors -----------------------------

    def get_all_categories(self) -> Dict[str, List[Transaction]]:
        """
        REQUIRES: nothing
        MODIFIES: nothing
        EFFECTS:  Returns a shallow copy of category → transactions mapping.
        """
        return {k: list(v) for k, v in self._categories.items()}

    # ----------------------------- Clear Helpers -----------------------------

    def clear_category(self, category: str) -> None:
        """
        REQUIRES: category is a string
        MODIFIES: self
        EFFECTS:  Empties the list for the category (unknown → MISCELLANEOUS).
        """
        key: str = (category or "").strip().upper()
        if key not in self._categories:
            key = "MISCELLANEOUS"
        self._categories[key].clear()

    def clear_all(self) -> None:
        """
        REQUIRES: nothing
        MODIFIES: self
        EFFECTS:  Empties every category list.
        """
        for key in self._categories:
            self._categories[key].clear()
