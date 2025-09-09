# File: ui/screens/transaction_scene.py

from __future__ import annotations

from typing import Dict, Optional, Tuple
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QMessageBox
)

from models.transaction import Transaction
from file_io.excel_loader import ExcelLoader
from utils.validator import (
    ValidationError,
    validate_month_name,
    validate_day_in_month,
    validate_slot_index,
    validate_transaction_or_none,
)


class TransactionScene(QDialog):
    """
    REQUIRES: QApplication is running; session_path points to an existing workbook.
    MODIFIES: In-memory working set; session file on save.
    EFFECTS:  Lets the user add or remove transactions for a given month/day/slot.
    """

    saved = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None, session_path: Optional[str] = None) -> None:
        super().__init__(parent)
        self.session_path: Optional[str] = session_path
        self._working_set: Dict[Tuple[str, int, int], Optional[Transaction]] = {}

        self.setWindowTitle("Edit Transactions")
        self.setModal(True)
        self.resize(900, 520)

        self.build_ui()
        self.populate_defaults()

    def build_ui(self) -> None:
        """
        REQUIRES: none
        MODIFIES: self
        EFFECTS:  Builds compact dialog controls for add/remove/save.
        """
        root = QVBoxLayout(self)

        grid = QGridLayout()
        r = 0

        grid.addWidget(QLabel("Month:"), r, 0)
        self.cmb_month = QComboBox()
        self.cmb_month.addItems([
            "JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE",
            "JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"
        ])
        grid.addWidget(self.cmb_month, r, 1)

        grid.addWidget(QLabel("Day:"), r, 2)
        self.spn_day = QSpinBox()
        self.spn_day.setRange(1, 31)
        grid.addWidget(self.spn_day, r, 3)

        grid.addWidget(QLabel("Slot (0/1):"), r, 4)
        self.cmb_slot = QComboBox()
        self.cmb_slot.addItems(["0", "1"])
        grid.addWidget(self.cmb_slot, r, 5)

        r += 1
        grid.addWidget(QLabel("Category:"), r, 0)
        self.cmb_category = QComboBox()
        self.cmb_category.addItems([
            "HOUSING", "TRANSPORTATION", "INSURANCE", "SCHOOL", "FOOD",
            "PERSONAL CARE", "SUBSCRIPTIONS", "HOLIDAY EXPENSES",
            "MISCELLANEOUS", "INCOME", "NONE"
        ])
        grid.addWidget(self.cmb_category, r, 1, 1, 3)

        grid.addWidget(QLabel("Type:"), r, 4)
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["EXPENSE", "INCOME", "NONE"])
        grid.addWidget(self.cmb_type, r, 5)

        r += 1
        grid.addWidget(QLabel("Amount:"), r, 0)
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setDecimals(2)
        self.spn_amount.setRange(0.00, 10_000_000.00)
        self.spn_amount.setSingleStep(1.00)
        grid.addWidget(self.spn_amount, r, 1)

        grid.addWidget(QLabel("Description:"), r, 2)
        self.txt_desc = QLineEdit()
        grid.addWidget(self.txt_desc, r, 3, 1, 3)

        root.addLayout(grid)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Add/Update")
        self.btn_remove = QPushButton("Remove")
        self.btn_save = QPushButton("Save")
        self.btn_close = QPushButton("Close")
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_remove)
        btns.addStretch(1)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_close)

        root.addLayout(btns)
        self.setLayout(root)

        self.btn_add.clicked.connect(self.on_add_clicked)
        self.btn_remove.clicked.connect(self.on_remove_clicked)
        self.btn_save.clicked.connect(self.on_save_clicked)
        self.btn_close.clicked.connect(self.close)

    def populate_defaults(self) -> None:
        """
        REQUIRES: none
        MODIFIES: widgets
        EFFECTS:  Sets initial values.
        """
        self.cmb_month.setCurrentIndex(0)
        self.spn_day.setValue(1)
        self.cmb_slot.setCurrentIndex(0)
        self.cmb_type.setCurrentIndex(0)
        self.spn_amount.setValue(0.00)
        self.cmb_category.setCurrentIndex(0)

    def current_key(self) -> Tuple[str, int, int]:
        """
        REQUIRES: controls contain valid values
        EFFECTS:  Returns (month_key, day, slot).
        """
        month_key = validate_month_name(self.cmb_month.currentText())
        day = int(self.spn_day.value())
        slot = int(self.cmb_slot.currentText())
        validate_slot_index(slot)
        return month_key, day, slot

    def none_checker(self, category_key: str, type_key: str) -> Optional[str]:
        """
        REQUIRES: category_key and type_key are uppercase keys from the combos
        MODIFIES: none
        EFFECTS:  Returns None if it's OK to proceed. Returns a short reason
                  string if the add/update should be blocked (not queued).
        """
        if type_key == "NONE" and category_key != "NONE":
            return "Type is NONE but Category is not NONE. Choose Category=NONE to clear a slot, or select a valid Type."
        return None

    def on_add_clicked(self) -> None:
        """
        REQUIRES: session_path is set; controls contain a valid tx or a clear op
        MODIFIES: _working_set
        EFFECTS:  Adds/updates a queued change. NONE+NONE queues a removal.
        """
        if not self.session_path:
            QMessageBox.warning(self, "No Session", "No active session found. Start a fresh or imported session first.")
            return

        month_key, day, slot = self.current_key()
        category_key = self.cmb_category.currentText().strip().upper()
        type_key = self.cmb_type.currentText().strip().upper()

        # NONE rules
        reason = self.none_checker(category_key, type_key)
        if reason:
            QMessageBox.information(self, "Not Queued", reason)
            return
        if type_key == "NONE" and category_key == "NONE":
            self._working_set[(month_key, day, slot)] = None
            QMessageBox.information(self, "Queued", "Clear operation queued for save.")
            return

        try:
            loader = ExcelLoader()
            loader.open(self.session_path)
            year = loader.get_year()
            validate_day_in_month(month_key, year, day)
            month_num = loader.month_to_number(month_key)
            loader.close()
        except Exception as e:
            QMessageBox.warning(self, "Invalid Day", str(e))
            return

        tx = Transaction(
            date=f"{year:04d}-{month_num:02d}-{day:02d}",
            day="",
            category=category_key,
            amount=float(self.spn_amount.value()),
            type=type_key,
            description=self.txt_desc.text().strip(),
        )

        try:
            validate_transaction_or_none(tx)
        except ValidationError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
            return

        self._working_set[(month_key, day, slot)] = tx
        QMessageBox.information(self, "Queued", "Transaction queued for save.")

    def on_remove_clicked(self) -> None:
        """
        REQUIRES: session_path is set
        MODIFIES: _working_set
        EFFECTS:  Queues a removal (None) for the selected month/day/slot.
        """
        if not self.session_path:
            QMessageBox.warning(self, "No Session", "No active session found. Start a fresh or imported session first.")
            return
        month_key, day, slot = self.current_key()
        self._working_set[(month_key, day, slot)] = None
        QMessageBox.information(self, "Queued", "Removal queued for save.")

    def on_save_clicked(self) -> None:
        """
        REQUIRES: session_path is set
        MODIFIES: session file
        EFFECTS:  Applies queued changes and saves workbook; emits saved.
        """
        if not self.session_path:
            QMessageBox.warning(self, "No Session", "No active session found. Start a fresh or imported session first.")
            return

        if not self._working_set:
            QMessageBox.information(self, "Nothing to Save", "There are no queued changes.")
            return

        try:
            loader = ExcelLoader()
            loader.open(self.session_path)
            for (month_key, day, slot), tx in self._working_set.items():
                loader.write_day_entry(month_key, day, slot, tx)
            loader.save()
            loader.close()
            self._working_set.clear()
            self.saved.emit()
            QMessageBox.information(self, "Saved", "Changes saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", str(e))
