from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any


class DatabaseClient:
    """Small DB-API helper for setup, cleanup, and data assertions."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> None:
        self.connection.execute(sql, tuple(params or ()))
        self.connection.commit()

    def fetch_one(
        self,
        sql: str,
        params: Iterable[Any] | None = None,
    ) -> dict[str, Any] | None:
        cursor = self.connection.execute(sql, tuple(params or ()))
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(cursor, row)

    def fetch_all(
        self,
        sql: str,
        params: Iterable[Any] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.connection.execute(sql, tuple(params or ()))
        return [_row_to_dict(cursor, row) for row in cursor.fetchall()]

    def scalar(self, sql: str, params: Iterable[Any] | None = None) -> Any:
        row = self.connection.execute(sql, tuple(params or ())).fetchone()
        if row is None:
            return None
        return row[0]

    def table_exists(self, table_name: str) -> bool:
        row = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type = ? AND name = ?",
            ("table", table_name),
        )
        return row is not None

    @contextmanager
    def transaction(self):
        try:
            yield self
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def close(self) -> None:
        self.connection.close()


def assert_record_exists(
    client: DatabaseClient,
    sql: str,
    params: Iterable[Any] | None = None,
) -> dict[str, Any]:
    record = client.fetch_one(sql, params)
    assert record is not None, f"Expected database query to return a record: {sql}"
    return record


def assert_row_count(
    client: DatabaseClient,
    sql: str,
    expected_count: int,
    params: Iterable[Any] | None = None,
) -> None:
    actual_count = client.scalar(sql, params)
    assert actual_count == expected_count, (
        f"Expected database row count {expected_count}, got {actual_count}. Query: {sql}"
    )


def assert_table_exists(client: DatabaseClient, table_name: str) -> None:
    assert client.table_exists(table_name), f"Expected database table to exist: {table_name}"


def _row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
    column_names = [description[0] for description in cursor.description or []]
    if hasattr(row, "keys"):
        return {key: row[key] for key in row.keys()}
    return dict(zip(column_names, row, strict=False))
