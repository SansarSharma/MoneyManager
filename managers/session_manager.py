# File: managers/session_manager.py
#
# (…header comments unchanged…)

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import shutil
import re

from file_io.excel_loader import ExcelLoader
from models.transaction import Transaction
from utils.validator import (
    ValidationError,
    validate_fresh_session_paths,
    validate_user_upload_path,
    validate_template_signature,
    validate_backup_directory,
    # Phase 2 addition:
    validate_upload_filesize,
)

@dataclass
class SessionState:
    """In-memory state for the currently active session."""
    session_path: Optional[str] = None
    mode: Optional[str] = None  # "FRESH" | "IMPORTED" | None


class SessionManager:
    """
    REQUIRES: filesystem layout with template and storage directories.
    MODIFIES: filesystem (session file creation/archiving), internal state.
    EFFECTS:  Orchestrates session lifecycle and paths.
    """

    # Filenames / dirs under template/
    TEMPLATE_FILE = "templateFile.xlsx"
    STORAGE_DIR = "file_storage"
    USER_DATA_FILE = "user_data.xlsx"
    BACKUPS_DIR = "backups"

    def __init__(self, project_root: Optional[str | Path] = None) -> None:
        # Default to repo root (…/money_manager)
        self._project_root: Path = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
        self._template_path: Path = self._project_root / "template" / self.TEMPLATE_FILE
        self._storage_dir: Path = self._project_root / "template" / self.STORAGE_DIR
        self._backups_dir: Path = self._storage_dir / self.BACKUPS_DIR
        self._user_data_path: Path = self._storage_dir / self.USER_DATA_FILE

        self._state: SessionState = SessionState()

    # ---------------------------- Public API ----------------------------

    def start_fresh_session(self) -> str:
        self.ensure_base_paths()
        self.archive_if_stale_exists(label="Stale")

        loader = ExcelLoader()
        session_path: str = loader.prepare_fresh_session(str(self._template_path), str(self._storage_dir))
        loader.close()

        self._state.session_path = session_path
        self._state.mode = "FRESH"
        return session_path

    def start_imported_session(self, source_path: str) -> str:
        self.ensure_base_paths()
        validate_user_upload_path(source_path)
        validate_upload_filesize(source_path)
        validate_template_signature(source_path)

        self.archive_if_stale_exists(label="Stale")

        loader = ExcelLoader()
        session_path: str = loader.prepare_fresh_session(str(self._template_path), str(self._storage_dir))
        loader.import_into_session(source_path)
        loader.close()

        self._state.session_path = session_path
        self._state.mode = "IMPORTED"
        return session_path

    def read_all(self) -> Dict[str, Dict[int, List[Optional[Transaction]]]]:
        self.require_active_session()
        loader = ExcelLoader()
        loader.open(self._state.session_path)  # type: ignore[arg-type]
        if not loader.verify_template():
            loader.close()
            raise ValidationError("Active session file no longer matches the template signature.")
        data = loader.read_all()
        loader.close()
        return data

    def write_all(self, data: Dict[str, Dict[int, List[Optional[Transaction]]]]) -> None:
        """
        REQUIRES: active session; data matches schema used by ExcelLoader.read_all()
        MODIFIES: session file
        EFFECTS:  Writes the provided working set to the workbook and saves it.
        """
        self.require_active_session()
        loader = ExcelLoader()
        loader.open(self._state.session_path)  # type: ignore[arg-type]
        if not loader.verify_template():
            loader.close()
            raise ValidationError("Active session file no longer matches the template signature.")
        loader.write_all(data)
        loader.save()
        loader.close()

    def save(self) -> None:
        self.require_active_session()
        loader = ExcelLoader()
        loader.open(self._state.session_path)  # type: ignore[arg-type]
        loader.save()
        loader.close()

    def save_backup(self, backup_dir: str) -> str:
        self.require_active_session()
        validate_backup_directory(backup_dir)
        loader = ExcelLoader()
        loader.open(self._state.session_path)  # type: ignore[arg-type]
        dst = loader.save_backup(backup_dir)
        loader.close()
        return dst

    def end_session_and_archive(self) -> Optional[str]:
        if not self.is_session_active():
            return None

        label: str = "Fresh" if self._state.mode == "FRESH" else "Imported" if self._state.mode == "IMPORTED" else "Prev"
        archived: str = self.archive_current_user_data(label=label)

        self._state = SessionState()
        return archived

    # -------- Small helpers exposed to UI code --------

    def get_session_path(self) -> Optional[str]:
        return self._state.session_path

    def get_mode(self) -> Optional[str]:
        return self._state.mode

    def is_session_active(self) -> bool:
        return bool(self._state.session_path and Path(self._state.session_path).exists())

    # ---------------------------- Internals ----------------------------

    def ensure_base_paths(self) -> None:
        validate_fresh_session_paths(str(self._template_path), str(self._storage_dir))
        self._backups_dir.mkdir(parents=True, exist_ok=True)

    def require_active_session(self) -> None:
        if not self.is_session_active():
            raise ValidationError("No active session. Start a fresh or imported session first.")

    def archive_if_stale_exists(self, label: str) -> None:
        if self._user_data_path.exists():
            try:
                _ = self.archive_current_user_data(label=label)
                self._state = SessionState()
                return
            except Exception:
                fallback: Path = self.unique_backup_name(prefix=f"User_Data_{label}")
                shutil.move(str(self._user_data_path), str(fallback))

    def archive_current_user_data(self, label: str) -> str:
        if not self._user_data_path.exists():
            raise ValidationError("No session file found to archive.")

        archived_path: Path = self.unique_backup_name(prefix=f"User_Data_{label}")
        shutil.move(str(self._user_data_path), str(archived_path))
        return str(archived_path)

    def unique_backup_name(self, prefix: str) -> Path:
        pattern = re.compile(re.escape(prefix) + r"_(\d+)\.xlsx$", re.IGNORECASE)
        max_n: int = 0
        for p in self._backups_dir.glob("*.xlsx"):
            m = pattern.match(p.name)
            if m:
                try:
                    n = int(m.group(1))
                    if n > max_n:
                        max_n = n
                except Exception:
                    pass
        next_n = max_n + 1
        return self._backups_dir / f"{prefix}_{next_n}.xlsx"
