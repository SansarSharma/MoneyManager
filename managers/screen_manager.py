# File: managers/screen_manager.py

from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox, QWidget

from managers.analytic_manager import AnalyticManager
from managers.session_manager import SessionManager
from notifications.concrete.budget_update_publisher import BudgetUpdatePublisher

try:
    from ui.screens.welcome_screen import WelcomeScreen
except Exception:
    WelcomeScreen = None  # type: ignore

try:
    from ui.screens.main_window import MainWindow
except Exception:
    MainWindow = None  # type: ignore


class ScreenManager(QObject):
    """
    REQUIRES: QApplication running in the process.
    MODIFIES: Top-level windows (Welcome, Main, Download, Transaction); shared services.
    EFFECTS:  Central controller for navigation, session lifecycle, and shared services.
    """

    def __init__(self, project_root: Optional[str | Path] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._session: SessionManager = SessionManager(project_root=project_root)
        self._welcome: Optional[QWidget] = None
        self._main: Optional[QWidget] = None
        self._download: Optional[QWidget] = None
        self._transaction: Optional[QWidget] = None

        self._publisher: BudgetUpdatePublisher = BudgetUpdatePublisher()
        self._analytics: AnalyticManager = AnalyticManager(session_path=None)

    def show_welcome(self) -> None:
        """
        REQUIRES: none
        MODIFIES: window stack
        EFFECTS:  Shows Welcome and closes Main/Download/Transaction.
        """
        if WelcomeScreen is None:
            QMessageBox.critical(None, "Missing Screen", "WelcomeScreen is not available.")
            return

        self.close_main()
        self.close_download()
        self.close_transaction()

        self._welcome = WelcomeScreen()
        setattr(self._welcome, "_screen_manager", self)
        self._welcome.setWindowTitle("Money Manager — Welcome")
        self._welcome.showMaximized()

    def start_session_fresh(self) -> None:
        """
        REQUIRES: template/storage valid
        MODIFIES: filesystem; window stack
        EFFECTS:  Starts new session and opens Main preloaded with it.
        """
        try:
            session_path: str = self._session.start_fresh_session()
        except Exception as e:
            QMessageBox.warning(None, "Session Error", str(e))
            return
        self.show_main(session_path=session_path)

    def start_session_imported(self, file_path: str) -> None:
        """
        REQUIRES: file_path is a valid template workbook
        MODIFIES: filesystem; window stack
        EFFECTS:  Starts imported session and opens Main preloaded with it.
        """
        try:
            session_path: str = self._session.start_imported_session(file_path)
        except Exception as e:
            QMessageBox.warning(None, "Import Error", str(e))
            return
        self.show_main(session_path=session_path)

    def show_main(self, session_path: Optional[str] = None) -> None:
        """
        REQUIRES: session_path provided or active session exists
        MODIFIES: window stack; analytics session path
        EFFECTS:  Creates Main with session_path set before showing and points analytics at it.
        """
        if MainWindow is None:
            QMessageBox.critical(None, "Missing Screen", "MainWindow is not available.")
            return

        resolved: Optional[str] = session_path or self._session.get_session_path()
        if not resolved:
            QMessageBox.warning(None, "No Session", "No active session to show.")
            return

        self._analytics.set_session_path(resolved)

        self.close_welcome()
        self.close_download()

        self._main = MainWindow(session_path=resolved)  # type: ignore[arg-type]
        setattr(self._main, "_screen_manager", self)
        self._main.setWindowTitle("Money Manager — Main")
        self._main.showMaximized()

    def show_transaction(self, session_path: Optional[str] = None) -> None:
        """
        REQUIRES: QApplication running; a valid session path is available.
        MODIFIES: window stack
        EFFECTS:  Opens the transaction scene for the active session and wires
                  a refresh callback to MainWindow after saves.
        """
        TransactionScene = self.import_transaction_scene_safe()
        if TransactionScene is None:
            QMessageBox.critical(None, "Missing Screen", "TransactionScene is not available.")
            return

        resolved = session_path or self._session.get_session_path()
        if not resolved:
            QMessageBox.warning(None, "No Session", "No active session found. Start a fresh or imported session first.")
            return

        if self._transaction is None:
            self._transaction = TransactionScene(parent=None, session_path=resolved)  # type: ignore[call-arg]
            if self._main is not None and hasattr(self._main, "load_session_into_lists"):
                self._transaction.saved.connect(self._main.load_session_into_lists)  # type: ignore[attr-defined]
            def _cleanup(_obj=None):
                self._transaction = None
            self._transaction.destroyed.connect(_cleanup)  # type: ignore[attr-defined]

        self._transaction.show()            # type: ignore[attr-defined]
        self._transaction.raise_()          # type: ignore[attr-defined]
        self._transaction.activateWindow()  # type: ignore[attr-defined]

    def request_finish_session(self) -> None:
        """
        REQUIRES: none
        MODIFIES: window stack
        EFFECTS:  Main -> Download (if present) else archive -> Welcome.
        """
        DownloadScreen: Optional[type[Any]] = self.import_download_screen_safe()
        if DownloadScreen is None:
            self.finish_session_and_go_welcome()
            return

        self.close_welcome()
        self.close_main()
        self.close_transaction()

        self._download = DownloadScreen()  # type: ignore[call-arg]
        setattr(self._download, "_screen_manager", self)
        self._download.setWindowTitle("Money Manager — Download")
        self._download.showMaximized()

    def finish_session_and_go_welcome(self) -> None:
        """
        REQUIRES: none
        MODIFIES: filesystem; window stack
        EFFECTS:  Archives current session, clears state, returns to Welcome.
        """
        try:
            self._session.end_session_and_archive()
        except Exception as e:
            QMessageBox.warning(None, "Archive Error", str(e))
        self.close_download()
        self.close_transaction()
        self.close_main()
        self.show_welcome()

    def get_session_path(self) -> Optional[str]:
        """
        EFFECTS: Returns absolute path of active session, else None.
        """
        return self._session.get_session_path()

    def is_session_active(self) -> bool:
        """
        EFFECTS: True iff a session file exists and is tracked.
        """
        return self._session.is_session_active()

    def get_mode(self) -> Optional[str]:
        """
        EFFECTS: Returns 'FRESH' | 'IMPORTED' | None.
        """
        return self._session.get_mode()

    def save(self) -> None:
        """
        MODIFIES: session file; publishes session:saved
        EFFECTS:  Flushes workbook to disk and notifies listeners of save.
        """
        try:
            self._session.save()
            path = self._session.get_session_path()
            if path:
                self._publisher.emit_session_saved(path)
        except Exception as e:
            QMessageBox.warning(None, "Save Error", str(e))

    def save_backup(self, backup_dir: str) -> Optional[str]:
        """
        REQUIRES: backup_dir writable
        MODIFIES: filesystem
        EFFECTS:  Writes a timestamped copy of the current session into backup_dir.
        """
        try:
            return self._session.save_backup(backup_dir)
        except Exception as e:
            QMessageBox.warning(None, "Backup Error", str(e))
            return None

    def import_download_screen_safe(self):
        """
        REQUIRES: none
        EFFECTS:  Returns DownloadScreen class if importable, else None.
        """
        try:
            from ui.screens.download_screen import DownloadScreen  # type: ignore
            return DownloadScreen
        except Exception:
            return None

    def import_transaction_scene_safe(self):
        """
        REQUIRES: none
        EFFECTS:  Returns TransactionScene class if importable, else None.
        """
        try:
            from ui.screens.transaction_scene import TransactionScene  # type: ignore
            return TransactionScene
        except Exception:
            return None

    def get_publisher(self) -> BudgetUpdatePublisher:
        """
        REQUIRES: none
        EFFECTS:  Returns the shared BudgetUpdatePublisher instance.
        """
        return self._publisher

    def get_analytics(self) -> AnalyticManager:
        """
        REQUIRES: none
        EFFECTS:  Returns the shared AnalyticManager instance.
        """
        return self._analytics

    def close_welcome(self) -> None:
        """
        MODIFIES: window stack
        EFFECTS:  Closes and clears Welcome reference.
        """
        if self._welcome is not None:
            try:
                self._welcome.close()
            finally:
                self._welcome = None

    def close_main(self) -> None:
        """
        MODIFIES: window stack
        EFFECTS:  Closes and clears Main reference.
        """
        if self._main is not None:
            try:
                self._main.close()
            finally:
                self._main = None

    def close_download(self) -> None:
        """
        MODIFIES: window stack
        EFFECTS:  Closes and clears Download reference.
        """
        if self._download is not None:
            try:
                self._download.close()
            finally:
                self._download = None

    def close_transaction(self) -> None:
        """
        MODIFIES: window stack
        EFFECTS:  Closes and clears Transaction reference.
        """
        if self._transaction is not None:
            try:
                self._transaction.close()
            finally:
                self._transaction = None