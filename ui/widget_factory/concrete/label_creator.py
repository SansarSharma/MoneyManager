# File: ui/widget_factory/concrete/label_creator.py
#
# Factory Method Pattern — Concrete Creator (QLabel).
#
# Abstraction Function:
# - Produces QLabel instances for titles, captions, or helper text.
#
# Representation Invariant:
# - text is a string; word_wrap controls multi-line behavior.

from typing import Optional, Any
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt
from ui.widget_factory.base.widget_creator_interface import WidgetCreatorInterface


class LabelCreator(WidgetCreatorInterface):
    def factory_method(
        self,
        text: str = "",
        align: int = Qt.AlignLeft,
        word_wrap: bool = True,
        object_name: Optional[str] = None,
        **_: Any
    ) -> QWidget:
        """
        REQUIRES: text is a string; align is a Qt alignment flag
        MODIFIES: label (internal state of returned widget)
        EFFECTS: Returns a configured QLabel
        """
        lbl: QLabel = QLabel(text)
        lbl.setAlignment(align)
        lbl.setWordWrap(word_wrap)
        if object_name:
            lbl.setObjectName(object_name)
        return lbl
