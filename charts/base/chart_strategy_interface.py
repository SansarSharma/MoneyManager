# File: charts/base/chart_strategy_interface.py
#
# Abstraction Function (AF):
# - Defines the Strategy interface for producing chart-ready series.
#
# Representation Invariant (RI):
# - Implementations must return a plain mapping {label -> value} in build_series().

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Protocol


Series = Dict[str, float]


class ChartStrategyInterface(ABC):
    """
    REQUIRES: An AnalyticManager will be provided to build_series().
    MODIFIES: none
    EFFECTS:  Strategy interface for chart data production independent of UI/toolkit.
    """

    @abstractmethod
    def get_title(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns a human-readable chart title.
        """
        raise NotImplementedError

    @abstractmethod
    def granularity(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns one of {"DAILY","WEEKLY","MONTHLY","YEARLY"}.
        """
        raise NotImplementedError

    @abstractmethod
    def build_series(self, analytic_manager) -> Series:
        """
        REQUIRES: analytic_manager provides the required aggregation method.
        MODIFIES: none
        EFFECTS:  Returns {label -> numeric value} for the chosen granularity.
        """
        raise NotImplementedError
