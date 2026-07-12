import json

import pytest

from utils.helpers.files import (
    assert_csv_headers,
    assert_csv_row_count,
    assert_json_file_field,
    read_csv_file,
    read_json_file,
)


pytestmark = pytest.mark.helpers


def test_csv_helpers_read_and_assert_headers_and_row_count(tmp_path):
    csv_path = tmp_path / "users.csv"
    csv_path.write_text("id,name\n1,Alex\n2,Sam\n", encoding="utf-8")

    assert read_csv_file(csv_path) == [
        {"id": "1", "name": "Alex"},
        {"id": "2", "name": "Sam"},
    ]
    assert_csv_headers(csv_path, ["id", "name"])
    assert_csv_row_count(csv_path, 2)


def test_csv_header_assertion_fails_with_clear_message(tmp_path):
    csv_path = tmp_path / "users.csv"
    csv_path.write_text("id,name\n1,Alex\n", encoding="utf-8")

    with pytest.raises(AssertionError, match="Expected CSV headers"):
        assert_csv_headers(csv_path, ["id", "email"])


def test_json_helpers_read_and_assert_nested_field(tmp_path):
    json_path = tmp_path / "user.json"
    json_path.write_text(
        json.dumps({"user": {"name": "Alex"}, "items": [{"id": 1}]}),
        encoding="utf-8",
    )

    assert read_json_file(json_path)["user"]["name"] == "Alex"
    assert_json_file_field(json_path, "user.name", "Alex")
    assert_json_file_field(json_path, "items.0.id", 1)
