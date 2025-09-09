# File: ui/widget_factory/concrete/widget_product.py
#
# Factory Method Pattern — Product.
#
# Abstraction Function:
# - Wraps a QWidget and exposes common operations used across screens
#   (naming, enabling, visibility, tooltip), so callers don’t care about
#   the concrete widget type.
#
# Representation Invariant:
# - _widget is a valid QWidget instance.
# - Accessors never return None; get_widget() always yields the wrapped QWidget.

from PyQt5.QtWidgets import QWidget


class WidgetProduct:
    """
    Represents the 'Product' in the Factory Method pattern.

    Typical usage:
        product = WidgetProduct(qwidget)
        layout.addWidget(product.get_widget())
        product.set_tooltip("Click me")
    """

    def __init__(self, widget: QWidget):
        """
        REQUIRES: widget is a valid QWidget
        MODIFIES: self
        EFFECTS: Stores the wrapped QWidget.
        """
        self._widget: QWidget = widget

    # ---------------- Core Accessor ----------------

    def get_widget(self) -> QWidget:
        """
        REQUIRES: nothing
        EFFECTS: Returns the underlying QWidget for adding to layouts.
        """
        return self._widget

    # ---------------- Convenience Mutators ----------------

    def set_object_name(self, name: str) -> None:
        """
        REQUIRES: name is a non-empty string
        MODIFIES: _widget
        EFFECTS: Sets the Qt objectName (useful for styling/tests).
        """
        self._widget.setObjectName(name)

    def set_tooltip(self, text: str) -> None:
        """
        REQUIRES: text is a string
        MODIFIES: _widget
        EFFECTS: Sets the tooltip shown on hover.
        """
        self._widget.setToolTip(text)

    def set_enabled(self, enabled: bool) -> None:
        """
        REQUIRES: enabled is a boolean
        MODIFIES: _widget
        EFFECTS: Enables or disables the widget.
        """
        self._widget.setEnabled(enabled)

    def set_visible(self, visible: bool) -> None:
        """
        REQUIRES: visible is a boolean
        MODIFIES: _widget
        EFFECTS: Shows or hides the widget.
        """
        self._widget.setVisible(visible)
