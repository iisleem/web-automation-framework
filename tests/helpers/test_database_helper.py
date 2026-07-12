import sqlite3

import pytest

from utils.helpers.database import (
    DatabaseClient,
    assert_record_exists,
    assert_row_count,
    assert_table_exists,
)


pytestmark = pytest.mark.helpers


def test_database_client_fetches_dict_rows():
    client = _client()
    client.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    client.execute("INSERT INTO users (name) VALUES (?)", ("Alex",))

    record = client.fetch_one("SELECT id, name FROM users WHERE name = ?", ("Alex",))

    assert record == {"id": 1, "name": "Alex"}


def test_database_client_fetch_all_and_scalar():
    client = _client()
    client.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    client.execute("INSERT INTO users (name) VALUES (?)", ("Alex",))
    client.execute("INSERT INTO users (name) VALUES (?)", ("Sam",))

    records = client.fetch_all("SELECT name FROM users ORDER BY name")

    assert records == [{"name": "Alex"}, {"name": "Sam"}]
    assert client.scalar("SELECT COUNT(*) FROM users") == 2


def test_database_assertions_validate_table_record_and_count():
    client = _client()
    client.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT)")
    client.execute("INSERT INTO orders (status) VALUES (?)", ("paid",))

    assert_table_exists(client, "orders")
    assert_record_exists(client, "SELECT * FROM orders WHERE status = ?", ("paid",))
    assert_row_count(client, "SELECT COUNT(*) FROM orders", 1)


def test_database_assertions_have_clear_failure_messages():
    client = _client()
    client.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT)")

    with pytest.raises(AssertionError, match="Expected database query"):
        assert_record_exists(client, "SELECT * FROM orders WHERE status = ?", ("paid",))

    with pytest.raises(AssertionError, match="Expected database row count"):
        assert_row_count(client, "SELECT COUNT(*) FROM orders", 1)


def test_database_transaction_rolls_back_on_failure():
    client = _client()
    client.execute("CREATE TABLE audit (id INTEGER PRIMARY KEY, event TEXT)")

    with pytest.raises(RuntimeError, match="boom"):
        with client.transaction():
            client.connection.execute("INSERT INTO audit (event) VALUES (?)", ("created",))
            raise RuntimeError("boom")

    assert client.scalar("SELECT COUNT(*) FROM audit") == 0


def _client():
    return DatabaseClient(sqlite3.connect(":memory:"))
