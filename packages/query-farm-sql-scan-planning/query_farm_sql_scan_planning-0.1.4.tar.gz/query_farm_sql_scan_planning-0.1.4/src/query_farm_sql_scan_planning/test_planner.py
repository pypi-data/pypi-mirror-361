import pytest
import datetime
import sqlglot
import pyarrow as pa
from .planner import RangeFieldInfo, SetFieldInfo, FileFieldInfo, Planner


@pytest.fixture
def sample_files() -> list[tuple[str, FileFieldInfo]]:
    return [
        (
            "file1",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(0),
                    max_value=pa.scalar(100),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(
                    values={pa.scalar("apple")}, has_nulls=False, has_non_nulls=True
                ),
                "t1": RangeFieldInfo(
                    min_value=pa.scalar(datetime.date(2023, 1, 1), pa.date32()),
                    max_value=pa.scalar(datetime.date(2024, 1, 1), pa.date32()),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
            },
        ),
        (
            "file2",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(150),
                    max_value=pa.scalar(300),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file3",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(250),
                    max_value=pa.scalar(450),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file4",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(400),
                    max_value=pa.scalar(600),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file5",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(550),
                    max_value=pa.scalar(750),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file6",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(700),
                    max_value=pa.scalar(900),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file7",
            {
                "v1": RangeFieldInfo(
                    min_value=pa.scalar(500),
                    max_value=pa.scalar(500),
                    has_nulls=False,
                    has_non_nulls=True,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
        (
            "file8",
            {
                "v1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
                "d1": SetFieldInfo(values=set(), has_nulls=False, has_non_nulls=False),
                "t1": RangeFieldInfo(
                    min_value=None,
                    max_value=None,
                    has_nulls=True,
                    has_non_nulls=False,
                ),
            },
        ),
    ]


ALL_FILES = set(
    {"file1", "file2", "file3", "file4", "file5", "file6", "file7", "file8"}
)


@pytest.mark.parametrize(
    "clause, expected_files",
    [
        ("t1 = DATE '2023-08-01'", {"file1"}),
        ("t1 > DATE '2023-08-01'", {"file1"}),
        ("t1 <> DATE '2023-08-01'", {"file1"}),
        ("t1 <> DATE '2023-08-01' - interval '6 days'", {"file1"}),
        # This isn't possible, to evaluate, we need to check for additional
        # column references on the right hand side that is not the source column,
        # it needs to distill down to a single scalar value.
        ("t1 <> DATE '2023-08-01' - interval (v1 || ' days')", ALL_FILES),
        ("t1 = DATE '1980-08-01'", set()),
        ("d1 = 'apple'", {"file1"}),
        (
            "d1 != 'apple'",
            {"file2", "file3", "file4", "file5", "file6", "file7", "file8"},
        ),
        ("d1 in ('apple')", {"file1"}),
        (
            "d1 not in ('apple')",
            {"file2", "file3", "file4", "file5", "file6", "file7", "file8"},
        ),
        ("'apple' in (d1)", ALL_FILES),  # could be improved.
        ("v1 < 100 and d1 = 'apple'", {"file1"}),
        ("v1 > 500 and v1 < 600", {"file4", "file5"}),
        ("v1 != 500 and v1 < 400", {"file1", "file2", "file3"}),
        ("v1 >= 300 and v1 <= 500", {"file2", "file3", "file4", "file7"}),
        ("v1 == 500", {"file4", "file7"}),
        ("v1 > 800 or v1 < 50", {"file6", "file1"}),
        ("v1 between 300 and 600", {"file3", "file4", "file5", "file2", "file7"}),
        ("v1 > 200 and v1 < 300", {"file2", "file3"}),
        ("not (v1 > 600)", {"file1", "file2", "file3", "file4", "file5", "file7"}),
        ("v1 > 600", {"file5", "file6"}),
        ("v1 > 10000", set()),
        ("v1 >= 150 and v1 <= 150", {"file2"}),
        (
            "v1 >= 0 and v1 <= 900",
            {"file1", "file2", "file3", "file4", "file5", "file6", "file7"},
        ),
        ("v1 < 0 and v1 > 1000", set()),
        ("false", set()),
        ("false and true", set()),
        ("true", ALL_FILES),
        ("not false", ALL_FILES),
        ("1 == 1", ALL_FILES),
        ("not (v1 < 0 and v1 > 1000)", ALL_FILES),
        ("v1 in (500)", set({"file4", "file7"})),
        (
            "v1 is not null",
            {"file1", "file2", "file3", "file4", "file5", "file6", "file7"},
        ),
        ("v1 is null", {"file8"}),
        ("v1 is null or v1 < 50", {"file8", "file1"}),
        ("v1 is not null and v1 < 50", {"file1"}),
        ("v1 in (75)", {"file1"}),
        ("v1 in (75, 500)", {"file1", "file4", "file7"}),
        ("v1 in (75,77722)", {"file1"}),
        ("v1 in (-2992)", set()),
        ("v1 in (-2992, -22922)", set()),
        (
            "v1 not between 200 and 1000",
            {"file1", "file2"},
        ),
        (
            "not (v1 not in (75, 500))",
            {"file1", "file4", "file7"},
        ),
        ("case when v1 < 200 then true else false end", {"file1", "file2"}),
        ("case when v1 < 200 then true end", {"file1", "file2"}),
        ("case when v1 = 500 then true end", {"file4", "file7"}),
        ("case when v1 = 500 then v1 = 500 end", {"file4", "file7"}),
        (
            "case when v1 = 50 then true when v1 = 500 then true end",
            {"file1", "file4", "file7"},
        ),
        ("case when v1 = 10001 then false else v1 = 500 end", {"file4", "file7"}),
        ("case when v1 in (500, 50) then true end", {"file4", "file7", "file1"}),
        (
            "v1 is distinct from 5",
            {"file1", "file2", "file3", "file4", "file5", "file6", "file7", "file8"},
        ),
        ("v1 - 50 = 1", {"file1"}),
        ("v1 - 50 < 200", {"file1", "file2"}),
        ("v1 * v1 < 200", ALL_FILES),
        ("200 > v1 * v1", ALL_FILES),
        ("abs(v1 - 500) < 100", ALL_FILES),  # Absolute difference
        ("v1 < 100 and abs(v1 - 500) < 100", ALL_FILES),  # Absolute difference
        ("v1 % 2 == 0", ALL_FILES),  # Even numbers
        (
            "v1 is not distinct from 5",
            {"file1"},
        ),
        ("50+v1 in (v1)", ALL_FILES),
        ("50 in (v1)", ALL_FILES),
        ("v1+50 in (100)", ALL_FILES),
        (
            "v1 not in (75, 500)",
            {"file1", "file2", "file3", "file4", "file5", "file6", "file7"},
        ),
        (
            "v1 is distinct from null",
            {"file1", "file2", "file3", "file4", "file5", "file6", "file7"},
        ),
        ("(v1, 50) in (v1, 100)", ALL_FILES),
        ("random() < 0.5", ALL_FILES),
        ("-v1 in (-50)", ALL_FILES),
        ("v1 in ()", set()),
        ("v1 not in ()", ALL_FILES),
        ("v1 in (null)", set()),
        ("null in (null)", set()),
        ("null not in (null)", set()),
        ("500 between v1 and 600", {"file1", "file2", "file3", "file4", "file7"}),
        ("500 between v1 and 600*-1", set()),
        ("v1 not between 300 and 600", {"file1", "file2", "file3", "file5", "file6"}),
        ("case when false then true end", set()),
        (
            "case when v1 = 500 then false else true end",
            {"file1", "file2", "file3", "file5", "file6", "file8"},
        ),
        ("case when v1 is null then true else false end", {"file8"}),
        ("v1 is null and v1 is not null", set()),
        ("v1 is null or v1 is not null", ALL_FILES),
        ("v1 = null", set()),
        ("null = null", set()),
    ],
)
def test_scan_planning(
    sample_files: list[tuple[str, FileFieldInfo]],
    clause: str,
    expected_files: set,
) -> None:
    """
    Test file filtering based on SQL clauses.

    Args:
        sample_files: List of files with their metadata
        clause: SQL clause to filter files
        expected_files: Set of filenames expected to pass the filter
    """
    # Create the filter
    filter_obj = Planner(sample_files)

    # Apply the filter
    result = set(
        filter_obj.get_matching_files(sqlglot.parse_one(clause, dialect="duckdb"))
    )

    # Check if files were filtered as expected
    if result != expected_files:
        # Create more detailed error message with diffing information
        missing = expected_files - result
        unexpected = result - expected_files
        error_msg = [f"Filter expression: {clause}"]

        if missing:
            error_msg.append(f"Missing files: {sorted(missing)}")
        if unexpected:
            error_msg.append(f"Unexpected files: {sorted(unexpected)}")

        error_msg.append(f"Expected: {sorted(expected_files)}")
        error_msg.append(f"Got: {sorted(result)}")

        assert result == expected_files, "\n".join(error_msg)
