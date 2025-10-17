from __future__ import annotations
from typing import Any, Optional
from app.db import session as db_session
import pandas as pd
import re


_TABLE_RE = re.compile(r"^[A-Za-z0-9_]+$")


class NotebookDB:
    """Lightweight, read-only DB helper exposed to notebook execution context.

    Only allows safe SELECT queries and simple table fetches. This keeps the
    notebook sandbox read-only by default. If you later want write access,
    add explicit checks and auditing.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        # SQLAlchemy engine (shared)
        self._engine = db_session.engine

    def _is_select(self, sql: str) -> bool:
        s = (sql or "").strip().lower()
        return s.startswith("select") or s.startswith("with")

    def execute_query(self, sql: str, params: Optional[dict] = None) -> pd.DataFrame:
        """Execute a read-only SQL query and return a pandas DataFrame.

        Raises PermissionError if the SQL appears non-SELECT.
        """
        if not self._is_select(sql):
            raise PermissionError("Only SELECT queries are allowed from notebook DB helper")
        # Use pandas read_sql_query which accepts SQLAlchemy engine
        return pd.read_sql_query(sql, con=self._engine, params=params)

    def fetch_table(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
        """Fetch a full table (limited) as a DataFrame. Table name must be safe.

        This method validates the table name to avoid SQL injection.
        """
        if not _TABLE_RE.match(table_name):
            raise ValueError("Invalid table name")
        sql = f"SELECT * FROM {table_name} LIMIT {int(limit)}"
        return self.execute_query(sql)

    # Convenience: return list of dict rows
    def fetch_rows(self, sql: str, params: Optional[dict] = None) -> list[dict]:
        df = self.execute_query(sql, params=params)
        return df.to_dict(orient="records")
