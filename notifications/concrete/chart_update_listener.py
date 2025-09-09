# File: notifications/concrete/chart_update_listener.py

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

from notifications.base.update_listener import UpdateListener
from notifications.concrete.budget_update_publisher import BudgetUpdatePublisher
from managers.analytic_manager import AnalyticManager


class ChartUpdateListener(UpdateListener):
    """
    REQUIRES: analytic_manager provides read-only summaries; on_refresh is callable
    MODIFIES: none (except UI via on_refresh)
    EFFECTS:  Reacts to budget/session events and triggers chart refresh.
    """

    def __init__(self, analytic_manager: AnalyticManager, on_refresh: Callable[[], None]) -> None:
        self._analytics: AnalyticManager = analytic_manager
        self._on_refresh: Callable[[], None] = on_refresh
        self._last_event: Optional[str] = None

    def update(self, event: str, payload: Mapping[str, Any] | None = None) -> None:
        """
        REQUIRES: event provided by a DataUpdatePublisher
        MODIFIES: none
        EFFECTS:  Records the event and calls on_refresh() so the UI/strategy
                  can rebuild based on new analytics data.
        """
        self._last_event = event

        # Heuristic: only refresh when data affecting charts changed.
        if event in {
            BudgetUpdatePublisher.EVENT_TRANSACTIONS_CHANGED,
            BudgetUpdatePublisher.EVENT_SESSION_SAVED,
            BudgetUpdatePublisher.EVENT_INCOME_CHANGED,
            BudgetUpdatePublisher.EVENT_YEAR_CHANGED,
        }:
            try:
                self._on_refresh()
            except Exception:
                # UI callback errors should not break notification flow.
                pass

    def get_last_event(self) -> Optional[str]:
        """
        REQUIRES: none
        EFFECTS:  Returns the last event key received, or None.
        """
        return self._last_event
