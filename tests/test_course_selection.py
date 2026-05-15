from datetime import date

import pytest

from canvas_download.course_selection import infer_archive_target, parse_number_selection, select_recent_courses


def test_infer_archive_target_uses_term_date_and_name() -> None:
    target = infer_archive_target(
        {
            "id": 123,
            "name": "ITM370 Combined",
            "term": {"name": "Fall 2024", "start_at": "2024-08-21T00:00:00Z"},
        }
    )

    assert target.course_id == "123"
    assert target.year == "2024"
    assert target.semester == "Fall"
    assert target.shell_name == "ITM370 Combined"


def test_select_recent_courses_filters_by_since_year() -> None:
    courses = [
        {"id": 1, "name": "Old", "term": {"name": "Spring 2021"}},
        {"id": 2, "name": "Recent", "term": {"name": "Spring 2023"}},
    ]

    targets = select_recent_courses(courses, years=4, today=date(2026, 5, 15), since_year=2022)

    assert [target.course_id for target in targets] == ["2"]


def test_parse_number_selection_supports_lists_ranges_and_all() -> None:
    assert parse_number_selection("1,3-5,2", total=6) == [0, 1, 2, 3, 4]
    assert parse_number_selection("all", total=3) == [0, 1, 2]
    assert parse_number_selection("", total=3) == []


def test_parse_number_selection_rejects_out_of_range_values() -> None:
    with pytest.raises(ValueError):
        parse_number_selection("4", total=3)
