# File: charts/concrete/daily_chart.py
#
# Abstraction Function (AF):
# - Strategy that returns category totals for a specific calendar day.
#
# Representation Invariant (RI):
# - year >= 1, 1 <= month <= 12, 1 <= day <= 31 (validation occurs upstream).

from __future__ import annotations

from typing import Dict

from charts.base.chart_strategy_interface import ChartStrategyInterface, Series


class DailyChart(ChartStrategyInterface):
    """
    REQUIRES: year/month/day correspond to a valid date in the open session.
    MODIFIES: none
    EFFECTS:  Produces category totals for the given day.
    """

    def __init__(self, year: int, month: int, day: int) -> None:
        self._year = int(year)
        self._month = int(month)
        self._day = int(day)

    def get_title(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns a title like 'Daily Totals — YYYY-MM-DD'.
        """
        return f"Daily Totals — {self._year:04d}-{self._month:02d}-{self._day:02d}"

    def granularity(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns 'DAILY'.
        """
        return "DAILY"

    def build_series(self, analytic_manager) -> Series:
        """
        REQUIRES: analytic_manager.get_category_totals_day(year, month, day)
        MODIFIES: none
        EFFECTS:  Returns {category -> amount} for the specified day.
        """
        return dict(
            analytic_manager.get_category_totals_day(self._year, self._month, self._day)
        )

