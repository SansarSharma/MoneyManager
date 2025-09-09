# File: ui/widget_factory/concrete/input_creator.py
#
# Factory Method Pattern — Concrete Creator (QLineEdit).
#
# Abstraction Function:
# - Produces QLineEdit inputs with optional placeholder and default text.
#
# Representation Invariant:
# - placeholder and text are strings; read_only is a boolean.

from typing import Optional, Any
from PyQt5.QtWidgets import QLineEdit, QWidget
from ui.widget_factory.base.widget_creator_interface import WidgetCreatorInterface


class InputCreator(WidgetCreatorInterface):
    def factory_method(
        self,
        placeholder: str = "",
        text: str = "",
        read_only: bool = False,
        object_name: Optional[str] = None,
        **_: Any
    ) -> QWidget:
        """
        REQUIRES: placeholder/text are strings
        MODIFIES: line_edit (internal state of returned widget)
        EFFECTS: Returns a configured QLineEdit
        """
        line_edit: QLineEdit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        if text:
            line_edit.setText(text)
        line_edit.setReadOnly(read_only)
        if object_name:
            line_edit.setObjectName(object_name)
        return line_edit
