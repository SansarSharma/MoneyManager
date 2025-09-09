# File: charts/concrete/weekly_chart.py
#
# Abstraction Function (AF):
# - Strategy that returns category totals for a given week within a month.
#
# Representation Invariant (RI):
# - week is a 1-based index within the selected month (validation occurs upstream).

from __future__ import annotations

from charts.base.chart_strategy_interface import ChartStrategyInterface, Series


class WeeklyChart(ChartStrategyInterface):
    """
    REQUIRES: week refers to a valid week index for the given month/year.
    MODIFIES: none
    EFFECTS:  Produces category totals aggregated over that week.
    """

    def __init__(self, year: int, month: int, week: int) -> None:
        self._year = int(year)
        self._month = int(month)
        self._week = int(week)

    def get_title(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns a title like 'Weekly Totals — YYYY-MM (Week W)'.
        """
        return f"Weekly Totals — {self._year:04d}-{self._month:02d} (Week {self._week})"

    def granularity(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns 'WEEKLY'.
        """
        return "WEEKLY"

    def build_series(self, analytic_manager) -> Series:
        """
        REQUIRES: analytic_manager.get_category_totals_week(year, month, week)
        MODIFIES: none
        EFFECTS:  Returns {category -> amount} for the specified week.
        """
        return dict(
            analytic_manager.get_category_totals_week(self._year, self._month, self._week)
        )
