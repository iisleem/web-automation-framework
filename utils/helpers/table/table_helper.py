from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def normalize_table_rows(rows: Sequence[Sequence[Any]]) -> list[list[str]]:
    return [[" ".join(str(cell).split()) for cell in row] for row in rows]


def find_row_by_cell_text(
    rows: Sequence[Sequence[Any]],
    text: str,
    exact: bool = False,
) -> list[str] | None:
    normalized_rows = normalize_table_rows(rows)
    for row in normalized_rows:
        for cell in row:
            if (exact and cell == text) or (not exact and text in cell):
                return row
    return None


def assert_table_contains_row(
    rows: Sequence[Sequence[Any]],
    expected_cells: Sequence[str],
) -> list[str]:
    normalized_rows = normalize_table_rows(rows)
    for row in normalized_rows:
        if all(expected in row for expected in expected_cells):
            return row
    raise AssertionError(f"Expected table to contain row with cells: {list(expected_cells)}")


def assert_column_sorted(
    rows: Sequence[Sequence[Any]],
    column_index: int,
    reverse: bool = False,
) -> list[str]:
    values = [row[column_index] for row in normalize_table_rows(rows)]
    expected = sorted(values, reverse=reverse)
    direction = "descending" if reverse else "ascending"
    assert values == expected, f"Expected column {column_index} to be sorted {direction}. Got {values}"
    return values


def extract_table_rows(table_locator) -> list[list[str]]:
    rows = table_locator.locator("tbody tr")
    extracted_rows: list[list[str]] = []
    for index in range(rows.count()):
        cells = rows.nth(index).locator("th, td").all_inner_texts()
        extracted_rows.append([" ".join(cell.split()) for cell in cells])
    return extracted_rows
