import pytest
from placecards import table_sort_key


def test_table_sorting_mixed_numeric_and_strings():
    # Mixed numeric and string table names
    input_tables = ["10", "2", "A", "AA", "ZZ", "1", "B"]

    # numeric ascending → 1, 2, 10
    # string ascending  → A, B, AA, ZZ
    expected = ["1", "2", "10", "A", "B", "AA", "ZZ"]

    assert sorted(input_tables, key=table_sort_key) == expected


def test_numeric_tables_sort_numerically():
    input_tables = ["10", "2", "1", "20", "3"]
    expected = ["1", "2", "3", "10", "20"]
    assert sorted(input_tables, key=table_sort_key) == expected


def test_string_tables_sort_lexicographically():
    input_tables = ["ZZ", "A", "AA", "B"]
    # Lexicographic ascending: A < B < AA < ZZ
    expected = ["A", "B", "AA", "ZZ"]
    assert sorted(input_tables, key=table_sort_key) == expected


def test_numeric_tables_come_before_strings():
    input_tables = ["B", "2", "A", "1"]
    expected = ["1", "2", "A", "B"]
    assert sorted(input_tables, key=table_sort_key) == expected

