# File: ui/screens/download_screen.py
#
# Abstraction Function (AF):
# - Provides end-of-session actions: save a copy of the current session file, finish, or go back to Main.
#
# Representation Invariant (RI):
# - _screen_manager is either None or a valid ScreenManager.
# - When finishing, ScreenManager handles archiving and navigation.

from typing import Optional
from pathlib import Path
import shutil

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

from utils.validator import validate_export_target_path


class DownloadScreen(QWidget):
    """
    REQUIRES: QApplication is running.
    MODIFIES: UI; optionally writes a copy of the session file.
    EFFECTS:  Allows user to export current session and/or finish the session.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._screen_manager = getattr(self, "_screen_manager", None)
        self._label_session = QLabel()
        self._label_mode = QLabel()
        self.build_ui()
        self.refresh_session_summary()
        self.wire_actions()

    def build_ui(self) -> None:
        """
        REQUIRES: none
        MODIFIES: self (layout/widgets)
        EFFECTS:  Builds the download/finish screen UI.
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Finish Session")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Session summary (file name + mode)
        self._label_session.setAlignment(Qt.AlignCenter)
        self._label_mode.setAlignment(Qt.AlignCenter)
        self._label_session.setStyleSheet("font-size: 13px;")
        self._label_mode.setStyleSheet("font-size: 13px; color: #555;")
        layout.addWidget(self._label_session)
        layout.addWidget(self._label_mode)

        layout.addSpacerItem(QSpacerItem(20, 24, QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Actions
        self.btn_save_copy = QPushButton("Save a Copy of Current Session…")
        self.btn_done = QPushButton("Home")
        self.btn_back_main = QPushButton("Go Back")

        for button in (self.btn_save_copy, self.btn_done, self.btn_back_main):
            button.setMinimumHeight(40)
            layout.addWidget(button)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

    def wire_actions(self) -> None:
        """
        REQUIRES: build_ui() created the buttons.
        MODIFIES: signal/slot connections.
        EFFECTS:  Connects buttons to handlers.
        """
        self.btn_save_copy.clicked.connect(self.on_save_copy)
        self.btn_done.clicked.connect(self.on_done)
        self.btn_back_main.clicked.connect(self.on_back_to_main)

    def refresh_session_summary(self) -> None:
        """
        REQUIRES: ScreenManager may be attached.
        EFFECTS:  Updates labels showing current session file name and mode.
        """
        session_path: Optional[str] = None
        mode: str = "—"

        if self._screen_manager:
            try:
                session_path = self._screen_manager.get_session_path()
                mode = (self._screen_manager.get_mode() or "—").title()
            except Exception:
                pass

        file_name = Path(session_path).name if session_path else "No active session"
        self._label_session.setText(f"Session File: {file_name}")
        self._label_mode.setText(f"Mode: {mode}")

    def on_save_copy(self) -> None:
        """
        REQUIRES: active session available via ScreenManager.
        MODIFIES: filesystem (writes a copy).
        EFFECTS:  Prompts for a destination and saves a copy of the session file.
        """
        if not self._screen_manager or not self._screen_manager.is_session_active():
            QMessageBox.warning(self, "Export", "No active session to export.")
            return

        session_path = self._screen_manager.get_session_path()
        if not session_path:
            QMessageBox.warning(self, "Export", "No active session file path.")
            return

        default_name = Path(session_path).name
        target_path, _ = QFileDialog.getSaveFileName(
            self, "Save Session As", default_name, "Excel Files (*.xlsx)"
        )
        if not target_path:
            return

        try:
            # Safer validator: includes "not in storage directory" guard.
            validate_export_target_path(target_path, session_path)
            shutil.copyfile(session_path, target_path)
            QMessageBox.information(self, "Saved", f"Session saved to:\n{target_path}")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save file.\n\n{e}")

    def on_done(self) -> None:
        """
        REQUIRES: ScreenManager injected.
        MODIFIES: filesystem (via SessionManager in ScreenManager); window stack.
        EFFECTS:  Archives session (Fresh/Imported) and returns to Welcome.
        """
        if not self._screen_manager:
            QMessageBox.warning(self, "Finish", "No screen manager attached.")
            return
        self._screen_manager.finish_session_and_go_welcome()

    def on_back_to_main(self) -> None:
        """
        REQUIRES: ScreenManager injected.
        EFFECTS:  Returns user to MainWindow without archiving.
        """
        from managers.screen_manager import ScreenManager  # local import to avoid cycles
        if not self._screen_manager or not isinstance(self._screen_manager, ScreenManager):
            self.close()
            return
        self._screen_manager.show_main()
