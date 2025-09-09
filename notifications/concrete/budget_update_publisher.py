# File: notifications/concrete/budget_update_publisher.py

from __future__ import annotations

from typing import Any, Mapping, Optional

from notifications.base.data_update_publisher import DataUpdatePublisher


class BudgetUpdatePublisher(DataUpdatePublisher):
    """
    REQUIRES: none
    MODIFIES: observers via notify()
    EFFECTS:  Specialized publisher for session and budget-related events.
    """

    EVENT_SESSION_SAVED = "session:saved"
    EVENT_TRANSACTIONS_CHANGED = "session:transactions_changed"
    EVENT_INCOME_CHANGED = "budget:income_changed"
    EVENT_YEAR_CHANGED = "budget:year_changed"

    def emit_session_saved(self, path: str) -> None:
        """
        REQUIRES: path is the absolute path to the saved workbook
        MODIFIES: observers
        EFFECTS:  Notifies that the session file has been flushed to disk.
        """
        self.notify(self.EVENT_SESSION_SAVED, {"path": path})

    def emit_transactions_changed(self, count: int | None = None) -> None:
        """
        REQUIRES: none
        MODIFIES: observers
        EFFECTS:  Notifies that queued transactions were written.
        """
        payload: Mapping[str, Any] = {"count": count} if count is not None else {}
        self.notify(self.EVENT_TRANSACTIONS_CHANGED, payload)

    def emit_income_changed(self, new_income: float) -> None:
        """
        REQUIRES: new_income >= 0
        MODIFIES: observers
        EFFECTS:  Notifies that the current income value changed.
        """
        self.notify(self.EVENT_INCOME_CHANGED, {"income": float(new_income)})

    def emit_year_changed(self, new_year: int) -> None:
        """
        REQUIRES: new_year is a 4-digit year
        MODIFIES: observers
        EFFECTS:  Notifies that the active year changed.
        """
        self.notify(self.EVENT_YEAR_CHANGED, {"year": int(new_year)})
