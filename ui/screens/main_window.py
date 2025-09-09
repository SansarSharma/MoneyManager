# File: ui/screens/main_window.py

from typing import Dict, List, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QListWidget, QListWidgetItem, QScrollArea, QSpacerItem, QSizePolicy
)

from ui.widget_factory.concrete.button_creator import ButtonCreator
from ui.widget_factory.concrete.label_creator import LabelCreator
from file_io.excel_loader import ExcelLoader
from utils.currency_formatter import format_currency


class MainWindow(QWidget):
    """
    REQUIRES: QApplication is running.
    MODIFIES: Qt UI state; reads the current session workbook (read-only).
    EFFECTS:  Shows categorized transaction lists for the active session.
    """

    def __init__(self, parent: Optional[QWidget] = None, session_path: Optional[str] = None) -> None:
        super().__init__(parent)
        self.session_path: Optional[str] = session_path
        self._screen_manager = getattr(self, "_screen_manager", None)

        self._category_lists: Dict[str, QListWidget] = {}
        self._categories: List[str] = [
            "HOUSING", "TRANSPORTATION", "INSURANCE", "SCHOOL", "FOOD",
            "PERSONAL CARE", "SUBSCRIPTIONS", "HOLIDAY EXPENSES", "MISCELLANEOUS",
            "INCOME", "NONE",
        ]

        self.build_ui()
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        self.load_session_into_lists()

    def build_ui(self) -> None:
        """
        REQUIRES: none
        MODIFIES: self
        EFFECTS:  Builds the main window layout and connects signals.
        """
        self.setObjectName("MainWindow")
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = LabelCreator().create(text="Money Manager — Categories", alignment=Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_host = QWidget()
        grid_layout = QGridLayout(grid_host)
        grid_layout.setContentsMargins(6, 6, 6, 6)
        grid_layout.setHorizontalSpacing(12)
        grid_layout.setVerticalSpacing(12)

        cols: int = 4
        for idx, name in enumerate(self._categories):
            r = idx // cols
            c = idx % cols
            box = self.build_category_box(name)
            grid_layout.addWidget(box, r, c)
        grid_layout.setRowStretch((len(self._categories) - 1) // cols + 1, 1)

        scroll.setWidget(grid_host)
        root.addWidget(scroll, 1)

        root.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Minimum))

        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        self.btn_profile = ButtonCreator().create(text="👤", min_width=72, min_height=56)
        bottom.addWidget(self.btn_profile, 0, Qt.AlignLeft)

        center_stack = QVBoxLayout()
        center_stack.setSpacing(8)
        self.btn_charts = ButtonCreator().create(text="View Charts", min_height=40)
        self.btn_ai = ButtonCreator().create(text="AI Assistant", min_height=40)
        self.btn_back = ButtonCreator().create(text="Home", min_height=40)
        center_stack.addWidget(self.btn_charts)
        center_stack.addWidget(self.btn_ai)
        center_stack.addWidget(self.btn_back)
        bottom.addStretch(1)
        bottom.addLayout(center_stack, 0)
        bottom.addStretch(1)

        self.btn_add = ButtonCreator().create(text="+", min_width=72, min_height=56)
        bottom.addWidget(self.btn_add, 0, Qt.AlignRight)

        self.btn_back.clicked.connect(self.on_home_clicked)
        self.btn_add.clicked.connect(self.on_add_clicked)

        root.addLayout(bottom)
        self.setLayout(root)
        self.setWindowTitle("Money Manager — Main")

    def on_home_clicked(self) -> None:
        """
        REQUIRES: ScreenManager injected
        MODIFIES: window stack via ScreenManager
        EFFECTS:  Initiates finish-session flow.
        """
        sm = getattr(self, "_screen_manager", None)
        if sm:
            sm.request_finish_session()

    def on_add_clicked(self) -> None:
        """
        REQUIRES: ScreenManager injected; session_path is set
        MODIFIES: window stack via ScreenManager
        EFFECTS:  Opens the transaction scene using the active session.
        """
        if not self.session_path:
            return
        sm = getattr(self, "_screen_manager", None)
        if sm:
            sm.show_transaction(self.session_path)

    def build_category_box(self, name: str) -> QGroupBox:
        """
        REQUIRES: category name key
        MODIFIES: self
        EFFECTS:  Returns a QGroupBox with a QListWidget placeholder.
        """
        box = QGroupBox(name)
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(8, 8, 8, 8)
        box_layout.setSpacing(6)

        lst = QListWidget()
        lst.setObjectName(f"list_{name.replace(' ', '_')}")
        lst.setMinimumHeight(140)
        lst.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        placeholder = QListWidgetItem("— No entries yet —")
        placeholder.setFlags(Qt.NoItemFlags)
        lst.addItem(placeholder)

        self._category_lists[name] = lst
        box_layout.addWidget(lst)
        return box

    def load_session_into_lists(self) -> None:
        """
        REQUIRES: session_path is set
        MODIFIES: UI lists
        EFFECTS:  Reads workbook and populates category lists.
        """
        if not self.session_path:
            return
        try:
            loader = ExcelLoader()
            loader.open(self.session_path)
            if not loader.verify_template():
                loader.close()
                return
            all_data = loader.read_all()
            loader.close()
        except Exception as e:
            print(f"[error] Failed to load session data: {e}")
            return

        for lst in self._category_lists.values():
            lst.clear()

        for _, days in all_data.items():
            for _, slots in days.items():
                for tx in slots:
                    if tx is None:
                        continue
                    target_name = (tx.category or "").strip().upper()
                    if tx.type.strip().upper() == "INCOME":
                        target_name = "INCOME"
                    if target_name not in self._category_lists:
                        target_name = "MISCELLANEOUS"

                    lst = self._category_lists[target_name]
                    amount_str = format_currency(tx.amount)
                    line = f"{tx.date}  •  {tx.day or '-'}  •  {amount_str}  •  {tx.type}  •  {tx.description or ''}"
                    lst.addItem(QListWidgetItem(line))

        for _, lst in self._category_lists.items():
            if lst.count() == 0:
                placeholder = QListWidgetItem("— No entries yet —")
                placeholder.setFlags(Qt.NoItemFlags)
                lst.addItem(placeholder)

    def get_category_list(self, name: str) -> QListWidget:
        """
        REQUIRES: name corresponds to a known category key
        EFFECTS:  Returns the QListWidget for that category.
        """
        return self._category_lists[name]
