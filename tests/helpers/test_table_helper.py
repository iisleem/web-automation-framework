import pytest

from utils.helpers.table import (
    assert_column_sorted,
    assert_table_contains_row,
    find_row_by_cell_text,
    normalize_table_rows,
)


pytestmark = pytest.mark.helpers


ROWS = [
    [" Name ", " Price "],
    ["Backpack", "$29.99"],
    ["Bike Light", "$9.99"],
]


def test_normalize_table_rows_collapses_cell_whitespace():
    assert normalize_table_rows([[" A   B ", "\nC "]]) == [["A B", "C"]]


def test_find_row_by_cell_text_supports_partial_and_exact_matching():
    assert find_row_by_cell_text(ROWS, "Bike") == ["Bike Light", "$9.99"]
    assert find_row_by_cell_text(ROWS, "Bike", exact=True) is None


def test_assert_table_contains_row_returns_matching_row():
    assert assert_table_contains_row(ROWS, ["Backpack", "$29.99"]) == ["Backpack", "$29.99"]


def test_assert_table_contains_row_fails_with_clear_message():
    with pytest.raises(AssertionError, match="Expected table"):
        assert_table_contains_row(ROWS, ["Missing"])


def test_assert_column_sorted_validates_sort_order():
    rows = [["A"], ["B"], ["C"]]

    assert assert_column_sorted(rows, 0) == ["A", "B", "C"]


def test_assert_column_sorted_fails_when_unsorted():
    rows = [["B"], ["A"]]

    with pytest.raises(AssertionError, match="sorted ascending"):
        assert_column_sorted(rows, 0)
