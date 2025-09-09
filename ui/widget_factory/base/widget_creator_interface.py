# File: ui/widget_factory/base/widget_creator_interface.py
#
# Factory Method Pattern — Creator (abstract).
#
# Abstraction Function:
# - Unifies how screens ask for widgets (Products) without tying UI code
#   to concrete PyQt classes or construction details.
#
# Representation Invariant:
# - Subclasses must implement factory_method(...) and return a QWidget.
# - The optional kwargs are passed straight through to the concrete creator.

from typing import Any
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget


class WidgetCreatorInterface(ABC):
    """
    Abstract Creator for UI widgets (Factory Method).
    """

    @abstractmethod
    def factory_method(self, **kwargs: Any) -> QWidget:
        """
        REQUIRES: kwargs accepted by the concrete creator
        EFFECTS: Returns a fully constructed QWidget (the Product)
        """
        raise NotImplementedError

    # Optional convenience for callers that want a common entry point.
    def create(self, **kwargs: Any) -> QWidget:
        """
        REQUIRES: kwargs accepted by the concrete creator
        EFFECTS: Calls factory_method and returns the widget
        """
        return self.factory_method(**kwargs)
