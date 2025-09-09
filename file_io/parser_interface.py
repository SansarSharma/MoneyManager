# File: file_io/parser_interface.py
#
# ParserInterface is the abstraction for all file adapters (Excel, CSV, etc.).
#
# Abstraction Function:
# - Unify how the application opens, reads, writes, and saves budget data
#   independent of the underlying file format.
#
# Representation Invariant:
# - A concrete implementation keeps an internal "open workbook" (or
#   equivalent handle) between open() and close()/object destruction.
# - All read_* and write_* methods assume the workbook is open.

from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from models.transaction import Transaction


class ParserInterface(ABC):
    """
    Abstract Adapter for persistence backends.
    """

    # ---------------- Lifecycle ----------------

    @abstractmethod
    def open(self, file_path: str) -> None:
        """
        REQUIRES: file_path points to an existing file (or a new path if the
                  implementation supports creating a new workbook)
        MODIFIES: internal state (stores open handle)
        EFFECTS:  Opens the file for subsequent reads/writes.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        REQUIRES: workbook is open
        MODIFIES: internal state
        EFFECTS:  Closes the file handle and releases resources.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_template(self) -> bool:
        """
        REQUIRES: workbook is open
        EFFECTS:  Returns True if the file matches the expected template signature.
        """
        raise NotImplementedError

    # ---------- Fixed fields (year / current income) ----------

    @abstractmethod
    def get_year(self) -> int:
        """EFFECTS: Returns the 4-digit year stored in the template."""
        raise NotImplementedError

    @abstractmethod
    def set_year(self, year: int) -> None:
        """MODIFIES: workbook; EFFECTS: Writes the year into the template."""
        raise NotImplementedError

    @abstractmethod
    def get_current_income(self) -> float:
        """EFFECTS: Returns the current income (non-negative)."""
        raise NotImplementedError

    @abstractmethod
    def set_current_income(self, income: float) -> None:
        """MODIFIES: workbook; EFFECTS: Writes the current income value."""
        raise NotImplementedError

    # ---------- Month/Day grid (two slots per day) ----------

    @abstractmethod
    def read_month(self, month_name: str) -> Dict[int, List[Optional[Transaction]]]:
        """
        REQUIRES: workbook is open; month_name is valid
        EFFECTS:  Reads all days for the month and returns:
                  day -> [slot0, slot1] (each slot is Transaction or None).
        """
        raise NotImplementedError

    @abstractmethod
    def write_day_entry(
        self, month_name: str, day: int, slot_index: int, tx: Optional[Transaction]
    ) -> None:
        """
        REQUIRES: workbook is open; arguments validated upstream
        MODIFIES: workbook
        EFFECTS:  Writes a single row for (month, day, slot). If tx is None,
                  clears or marks as 'NONE'.
        """
        raise NotImplementedError

    @abstractmethod
    def read_all(self) -> Dict[str, Dict[int, List[Optional[Transaction]]]]:
        """EFFECTS: Reads the entire year: { month -> { day -> [slot0, slot1] } }"""
        raise NotImplementedError

    @abstractmethod
    def write_all(self, data: Dict[str, Dict[int, List[Optional[Transaction]]]]) -> None:
        """MODIFIES: workbook; EFFECTS: Writes all months/days/slots."""
        raise NotImplementedError

    # ---------- Persistence ----------

    @abstractmethod
    def save(self) -> None:
        """MODIFIES: workbook file; EFFECTS: Saves changes to the same file."""
        raise NotImplementedError

    @abstractmethod
    def save_as(self, file_path: str) -> None:
        """MODIFIES: filesystem; EFFECTS: Saves changes to a new file path."""
        raise NotImplementedError

    # ---------- Session helpers ----------

    @abstractmethod
    def get_path(self) -> Optional[str]:
        """
        EFFECTS: Returns the absolute filesystem path of the currently-open
                 workbook, or None if no workbook is open.
        """
        raise NotImplementedError

    @abstractmethod
    def save_backup(self, backup_dir: str) -> str:
        """
        REQUIRES: workbook is open
        MODIFIES: filesystem
        EFFECTS:  Writes a timestamped copy of the open workbook into backup_dir.
                  RETURNS: Full path to the created backup file.
        """
        raise NotImplementedError

    @abstractmethod
    def prepare_fresh_session(self, template_path: str, storage_dir: str) -> str:
        """
        REQUIRES: template_path exists; storage_dir writable
        MODIFIES: filesystem
        EFFECTS:  Copies the template into storage_dir as 'user_data.xlsx',
                  opens it, and RETURNS its full path.
        """
        raise NotImplementedError

    @abstractmethod
    def import_into_session(self, source_path: str) -> None:
        """
        REQUIRES: workbook is open; source_path is a valid template
        MODIFIES: workbook file
        EFFECTS:  Replaces the current session file with source_path contents
                  (after verification), then re-opens it.
        """
        raise NotImplementedError
