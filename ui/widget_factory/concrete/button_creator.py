# File: ui/widget_factory/concrete/button_creator.py
#
# Factory Method Pattern — Concrete Creator (QPushButton).
#
# Abstraction Function:
# - Produces QPushButton instances configured from simple keyword args.
#
# Representation Invariant:
# - text is a non-empty string for visible buttons.
# - on_click is either None or a callable taking no arguments.

from typing import Optional, Callable, Any
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtCore import Qt
from ui.widget_factory.base.widget_creator_interface import WidgetCreatorInterface


class ButtonCreator(WidgetCreatorInterface):
    def factory_method(
        self,
        text: str = "Button",
        on_click: Optional[Callable[[], None]] = None,
        tooltip: Optional[str] = None,
        object_name: Optional[str] = None,
        enabled: bool = True,
        **_: Any
    ) -> QWidget:
        """
        REQUIRES: text is a string; on_click is callable or None
        MODIFIES: button (internal state of returned widget)
        EFFECTS: Returns a configured QPushButton
        """
        btn: QPushButton = QPushButton(text)
        btn.setEnabled(enabled)
        if tooltip:
            btn.setToolTip(tooltip)
        if object_name:
            btn.setObjectName(object_name)
        if on_click is not None:
            btn.clicked.connect(on_click)
        btn.setCursor(Qt.PointingHandCursor)
        return btn
