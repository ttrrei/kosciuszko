"""Database operator for Oracle-backed ingestion workflows."""

from __future__ import annotations

import sys
import types
from importlib.util import find_spec
from typing import Any

from src.config import Config


if find_spec("oracledb") is not None:
    import oracledb
else:
    oracledb = types.ModuleType("oracledb")

    class _OracleDbError(Exception):
        """Fallback Oracle error used when python-oracledb is unavailable."""

    def _missing_create_pool(*_args: Any, **_kwargs: Any) -> Any:
        raise _OracleDbError(
            "python-oracledb is required to create an Oracle connection pool."
        )

    oracledb.Error = _OracleDbError
    oracledb.create_pool = _missing_create_pool
    sys.modules["oracledb"] = oracledb


class DbOperator:
    """Singleton Oracle database operator with chunked merge execution."""

    _instance = None
    _pool = None

    def __new__(cls):
        """Return the single DbOperator instance used by the process."""
        if cls._instance is None:
            cls._instance = super(DbOperator, cls).__new__(cls)
            cls._instance._config = Config()
        return cls._instance

    def _get_pool(self):
        """Lazily initialize and return the Oracle connection pool."""
        if self._pool is None:
            try:
                self._pool = oracledb.create_pool(
                    user=self._config.DB_USER,
                    password=self._config.DB_PASSWORD,
                    dsn=self._config.DB_DSN,
                    min=1,
                    max=2,
                    increment=1,
                    wallet_location=self._config.WALLET_LOCATION,
                    wallet_password=self._config.WALLET_PASSWORD,
                )
            except oracledb.Error as exc:
                raise ConnectionError(f"无法创建 Oracle 连接池: {exc}") from exc
        return self._pool

    def get_connection(self):
        """Acquire one connection from the singleton pool."""
        return self._get_pool().acquire()

    def execute_merge(
        self,
        sql: str | None = None,
        data: list[dict[str, Any]] | None = None,
        *,
        target_table: str | None = None,
        primary_keys: list[str] | None = None,
    ) -> None:
        """Execute merge operations in BATCH_SIZE chunks.

        Args:
            sql: SQL statement to pass to ``cursor.executemany``.
            data: Records to merge.
            target_table: Compatibility alias used by early tests while the
                final MERGE SQL builder is still evolving.
            primary_keys: Optional business keys supplied by profile-driven
                scrapers for future MERGE SQL generation.
        """
        if not data:
            return

        merge_sql = sql if sql is not None else target_table
        if merge_sql is None:
            raise ValueError("execute_merge requires either sql or target_table.")

        batch_size = self._config.BATCH_SIZE
        if batch_size <= 0:
            raise ValueError("BATCH_SIZE 必须为正整数。")

        for start in range(0, len(data), batch_size):
            chunk = data[start : start + batch_size]
            self._raw_merge_execute(merge_sql, chunk)

    def _raw_merge_execute(self, sql: str, chunk: list[dict[str, Any]]) -> None:
        """Execute a single chunk against Oracle.

        This method is intentionally small so tests can replace it with a mock
        when validating chunking behavior.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, chunk)
            conn.commit()
        except oracledb.Error:
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._pool.release(conn)

    def close(self) -> None:
        """Close the Oracle connection pool if it has been initialized."""
        if self._pool:
            self._pool.close()
            self._pool = None
