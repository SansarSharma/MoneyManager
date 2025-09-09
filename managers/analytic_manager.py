# File: managers/analytic_manager.py

from __future__ import annotations

from typing import Dict, List, Optional, Iterable, Tuple
from datetime import datetime, date

from file_io.excel_loader import ExcelLoader
from models.transaction import Transaction
from models.financial_summary import FinancialSummary
from utils.validator import ValidationError


class AnalyticManager:
    """
    REQUIRES: Excel session workbook created by SessionManager and compatible with ExcelLoader.
    MODIFIES: none (read-only manager)
    EFFECTS:  Provides read-only analytics over the active session to power charts/summary.
    """

    def __init__(self, session_path: Optional[str] = None) -> None:
        """
        REQUIRES: session_path is None or points to an existing workbook file.
        MODIFIES: self
        EFFECTS:  Initializes the manager with an optional session path.
        """
        self._session_path: Optional[str] = session_path

    # ------------ Session wiring ------------

    def set_session_path(self, session_path: str) -> None:
        """
        REQUIRES: session_path points to an existing workbook file.
        MODIFIES: self
        EFFECTS:  Updates the active session path.
        """
        self._session_path = session_path

    def get_session_path(self) -> Optional[str]:
        """
        EFFECTS: Returns the current session path, else None.
        """
        return self._session_path

    def require_active_session(self) -> str:
        """
        REQUIRES: none
        EFFECTS:  Returns the active session path or raises if missing.
        """
        if not self._session_path:
            raise ValidationError("No active session. Set session path first.")
        return self._session_path

    # ------------ Summary / top-level ------------

    def get_year(self) -> int:
        """
        REQUIRES: active session
        EFFECTS:  Returns the workbook's year value.
        """
        path = self.require_active_session()
        loader = ExcelLoader()
        loader.open(path)
        year = loader.get_year()
        loader.close()
        return year

    def compute_financial_summary(self) -> FinancialSummary:
        """
        REQUIRES: active session
        EFFECTS:  Aggregates totals for the whole workbook year and returns a FinancialSummary.
        """
        year = self.get_year()

        totals = self.get_monthly_series()  # [{month_key, income, expense, net}, ...]
        total_income = sum(m["income"] for m in totals)
        total_expense = sum(m["expense"] for m in totals)
        net = total_income - total_expense

        return FinancialSummary(
            year=year,
            total_income=total_income,
            total_expense=total_expense,
            net_savings=net,
            notes=None,
        )

    # ------------ Series + slices for charts ------------

    def get_month_totals(self, month_key: str) -> Dict[str, float]:
        """
        REQUIRES: active session; month_key is a valid template month name (e.g., 'JANUARY')
        EFFECTS:  Returns {'income': x, 'expense': y, 'net': x - y} for the given month.
        """
        txs = self._iter_month_transactions(month_key)
        income = sum(t.amount for t in txs if t.type.strip().upper() == "INCOME")
        expense = sum(t.amount for t in txs if t.type.strip().upper() == "EXPENSE")
        return {"income": income, "expense": expense, "net": income - expense}

    def get_monthly_series(self) -> List[Dict[str, float]]:
        """
        REQUIRES: active session
        EFFECTS:  Returns a list of dicts in template order:
                  [{'month': 'JANUARY', 'income': ..., 'expense': ..., 'net': ...}, ...]
        """
        path = self.require_active_session()
        loader = ExcelLoader()
        loader.open(path)
        months = loader.months_in_order()
        loader.close()

        series: List[Dict[str, float]] = []
        for m in months:
            t = self.get_month_totals(m)
            series.append({"month": m, "income": t["income"], "expense": t["expense"], "net": t["net"]})
        return series

    def get_daily_series(self, month_key: str) -> List[Dict[str, float]]:
        """
        REQUIRES: active session; valid month_key
        EFFECTS:  Returns daily income/expense for a month as:
                  [{'date': 'YYYY-MM-DD', 'income': x, 'expense': y, 'net': x - y}, ...]
        """
        txs = list(self._iter_month_transactions(month_key))
        by_day: Dict[str, Dict[str, float]] = {}
        for t in txs:
            d = t.date
            if d not in by_day:
                by_day[d] = {"income": 0.0, "expense": 0.0}
            if t.type.strip().upper() == "INCOME":
                by_day[d]["income"] += t.amount
            elif t.type.strip().upper() == "EXPENSE":
                by_day[d]["expense"] += t.amount

        # Sort by date ascending
        items = []
        for d in sorted(by_day.keys(), key=lambda s: self._safe_date_key(s)):
            inc = by_day[d]["income"]
            exp = by_day[d]["expense"]
            items.append({"date": d, "income": inc, "expense": exp, "net": inc - exp})
        return items

    def get_weekly_series(self, month_key: str) -> List[Dict[str, float]]:
        """
        REQUIRES: active session; valid month_key
        EFFECTS:  Buckets the month by ISO week:
                  [{'iso_week': 'YYYY-Www', 'income': x, 'expense': y, 'net': x - y}, ...]
        """
        txs = list(self._iter_month_transactions(month_key))
        buckets: Dict[str, Dict[str, float]] = {}
        for t in txs:
            dt = self._safe_parse_date(t.date)
            iso_label = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
            if iso_label not in buckets:
                buckets[iso_label] = {"income": 0.0, "expense": 0.0}
            if t.type.strip().upper() == "INCOME":
                buckets[iso_label]["income"] += t.amount
            elif t.type.strip().upper() == "EXPENSE":
                buckets[iso_label]["expense"] += t.amount

        items = []
        for k in sorted(buckets.keys()):
            inc = buckets[k]["income"]
            exp = buckets[k]["expense"]
            items.append({"iso_week": k, "income": inc, "expense": exp, "net": inc - exp})
        return items

    def get_category_totals_year(self) -> Dict[str, float]:
        """
        REQUIRES: active session
        EFFECTS:  Returns total EXPENSE by category for the whole year
                  (INCOME is excluded from category rollups by design).
        """
        totals: Dict[str, float] = {}
        for t in self._iter_all_transactions():
            ttype = t.type.strip().upper()
            if ttype != "EXPENSE":
                continue
            key = (t.category or "").strip().upper() or "MISCELLANEOUS"
            totals[key] = totals.get(key, 0.0) + t.amount
        return totals

    def get_income_vs_expense_year(self) -> Dict[str, float]:
        """
        REQUIRES: active session
        EFFECTS:  Returns {'income': total_income, 'expense': total_expense, 'net': net}.
        """
        income = 0.0
        expense = 0.0
        for t in self._iter_all_transactions():
            ttype = t.type.strip().upper()
            if ttype == "INCOME":
                income += t.amount
            elif ttype == "EXPENSE":
                expense += t.amount
        return {"income": income, "expense": expense, "net": income - expense}

    # ------------ Internals ------------

    def _iter_all_transactions(self) -> Iterable[Transaction]:
        """
        REQUIRES: active session
        EFFECTS:  Yields every Transaction in the workbook (skips Nones/invalid).
        """
        path = self.require_active_session()
        loader = ExcelLoader()
        loader.open(path)
        if not loader.verify_template():
            loader.close()
            return  # empty generator
        all_data = loader.read_all()
        loader.close()

        for _, days in all_data.items():
            for _, slots in days.items():
                for tx in slots:
                    if tx is None:
                        continue
                    ttype = (tx.type or "").strip().upper()
                    if ttype not in {"EXPENSE", "INCOME"}:
                        continue
                    yield tx

    def _iter_month_transactions(self, month_key: str) -> Iterable[Transaction]:
        """
        REQUIRES: active session; valid month_key
        EFFECTS:  Yields Transactions for a given month (skips Nones/invalid).
        """
        path = self.require_active_session()
        loader = ExcelLoader()
        loader.open(path)
        # Validate by attempting read; ExcelLoader validates month name internally
        month_data = loader.read_month(month_key)
        loader.close()

        for _, slots in month_data.items():
            for tx in slots:
                if tx is None:
                    continue
                ttype = (tx.type or "").strip().upper()
                if ttype not in {"EXPENSE", "INCOME"}:
                    continue
                yield tx

    def _safe_date_key(self, datestr: str) -> Tuple[int, int, int]:
        """
        REQUIRES: datestr is 'YYYY-MM-DD' or similar
        EFFECTS:  Returns a tuple (Y, M, D) for sorting; falls back to (9999,12,31).
        """
        try:
            dt = self._safe_parse_date(datestr)
            return (dt.year, dt.month, dt.day)
        except Exception:
            return (9999, 12, 31)

    def _safe_parse_date(self, datestr: str) -> date:
        """
        REQUIRES: datestr is 'YYYY-MM-DD'
        EFFECTS:  Returns a date object; raises on failure.
        """
        return datetime.strptime(str(datestr), "%Y-%m-%d").date()
