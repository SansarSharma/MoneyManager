# File: charts/concrete/monthly_chart.py
#
# Abstraction Function (AF):
# - Strategy that returns category totals for a given month.
#
# Representation Invariant (RI):
# - year >= 1, 1 <= month <= 12.

from __future__ import annotations

from charts.base.chart_strategy_interface import ChartStrategyInterface, Series


class MonthlyChart(ChartStrategyInterface):
    """
    REQUIRES: year/month exist in the active session.
    MODIFIES: none
    EFFECTS:  Produces category totals aggregated over the month.
    """

    def __init__(self, year: int, month: int) -> None:
        self._year = int(year)
        self._month = int(month)

    def get_title(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns a title like 'Monthly Totals — YYYY-MM'.
        """
        return f"Monthly Totals — {self._year:04d}-{self._month:02d}"

    def granularity(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns 'MONTHLY'.
        """
        return "MONTHLY"

    def build_series(self, analytic_manager) -> Series:
        """
        REQUIRES: analytic_manager.get_category_totals_month(year, month)
        MODIFIES: none
        EFFECTS:  Returns {category -> amount} for the specified month.
        """
        return dict(
            analytic_manager.get_category_totals_month(self._year, self._month)
        )
