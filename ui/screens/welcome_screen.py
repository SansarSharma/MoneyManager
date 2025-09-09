# File: ui/screens/welcome_screen.py
#
# Abstraction Function (AF):
# - Presents the entry point UI: start a fresh session, import a file, or download the template.
# - Delegates navigation and session lifecycle to ScreenManager injected as _screen_manager.
#
# Representation Invariant (RI):
# - _screen_manager is either None or a valid ScreenManager instance.
# - UI buttons are connected to event handlers after construction.

from typing import Optional
from pathlib import Path
import shutil

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from ui.widget_factory.concrete.button_creator import ButtonCreator
from ui.widget_factory.concrete.label_creator import LabelCreator

from utils.validator import ValidationError, validate_download_target_path


class WelcomeScreen(QWidget):
    """
    REQUIRES: QApplication is running.
    MODIFIES: Qt UI state (this window).
    EFFECTS:  Provides actions to start/import a session or download the template.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._screen_manager = getattr(self, "_screen_manager", None)  # injected externally
        self.build_ui()
        self.wire_actions()

    # ---------------- UI ----------------

    def build_ui(self) -> None:
        """
        REQUIRES: none
        MODIFIES: self (layout/widgets)
        EFFECTS:  Builds the welcome screen UI.
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        pixmap = QPixmap("resources/logo.png")
        logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        title_label = LabelCreator().create(text="Welcome to Money Manager", alignment=Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title_label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.btn_continue = ButtonCreator().create(text="Continue Without File", min_height=40)
        self.btn_upload = ButtonCreator().create(text="Upload Excel File", min_height=40)
        self.btn_download_template = ButtonCreator().create(text="Download Template", min_height=40)

        for btn in (self.btn_continue, self.btn_upload, self.btn_download_template):
            layout.addWidget(btn)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

    def wire_actions(self) -> None:
        """
        REQUIRES: build_ui() has created buttons.
        MODIFIES: signal/slot connections.
        EFFECTS:  Connects buttons to event handlers.
        """
        self.btn_continue.clicked.connect(self.on_continue_without_file)
        self.btn_upload.clicked.connect(self.on_upload_excel)
        self.btn_download_template.clicked.connect(self.on_download_template)

    # ---------------- Paths (for template download convenience) ----------------

    def project_root(self) -> Path:
        """
        REQUIRES: codebase layout matches repo structure.
        EFFECTS:  Returns repository root path.
        """
        return Path(__file__).resolve().parents[2]  # ui/screens -> ui -> repo root

    def template_path(self) -> Path:
        """
        EFFECTS: Returns absolute path to the built-in Excel template.
        """
        return self.project_root() / "template" / "templateFile.xlsx"

    # ---------------- Actions ----------------

    def on_continue_without_file(self) -> None:
        """
        REQUIRES: ScreenManager injected.
        EFFECTS:  Starts a fresh session via ScreenManager.
        """
        if not self._screen_manager:
            QMessageBox.warning(self, "Navigation", "No screen manager attached.")
            return
        self._screen_manager.start_session_fresh()

    def on_upload_excel(self) -> None:
        """
        REQUIRES: ScreenManager injected.
        MODIFIES: filesystem (through ScreenManager).
        EFFECTS:  Prompts for a workbook and starts an imported session.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel Template", "", "Excel Files (*.xlsx);;All Files (*)"
        )
        if not file_path:
            return
        if not self._screen_manager:
            QMessageBox.warning(self, "Navigation", "No screen manager attached.")
            return
        self._screen_manager.start_session_imported(file_path)

    def on_download_template(self) -> None:
        """
        REQUIRES: template exists.
        MODIFIES: filesystem (writes a copy).
        EFFECTS:  Saves a copy of the built-in template to a user-selected path.
        """
        default_name = "MoneyManager_Template.xlsx"
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Save Template As", default_name, "Excel Files (*.xlsx)"
        )
        if not target_path:
            return
        try:
            validate_download_target_path(target_path)
            src = self.template_path()
            if not src.exists():
                raise FileNotFoundError(f"Template not found at: {src}")
            shutil.copyfile(str(src), target_path)
            QMessageBox.information(self, "Template Saved", f"Template saved to:\n{target_path}")
        except ValidationError as ve:
            QMessageBox.warning(self, "Save Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save the template.\n\n{e}")
