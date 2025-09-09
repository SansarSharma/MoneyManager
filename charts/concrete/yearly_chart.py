# File: charts/concrete/yearly_chart.py
#
# Abstraction Function (AF):
# - Strategy that returns category totals for a given year.
#
# Representation Invariant (RI):
# - year >= 1.

from __future__ import annotations

from charts.base.chart_strategy_interface import ChartStrategyInterface, Series


class YearlyChart(ChartStrategyInterface):
    """
    REQUIRES: year exists in the active session.
    MODIFIES: none
    EFFECTS:  Produces category totals aggregated over the year.
    """

    def __init__(self, year: int) -> None:
        self._year = int(year)

    def get_title(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns a title like 'Yearly Totals — YYYY'.
        """
        return f"Yearly Totals — {self._year:04d}"

    def granularity(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns 'YEARLY'.
        """
        return "YEARLY"

    def build_series(self, analytic_manager) -> Series:
        """
        REQUIRES: analytic_manager.get_category_totals_year(year)
        MODIFIES: none
        EFFECTS:  Returns {category -> amount} for the specified year.
        """
        return dict(
            analytic_manager.get_category_totals_year(self._year)
        )
