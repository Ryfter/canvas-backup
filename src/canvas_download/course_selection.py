from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Any


SEMESTER_ALIASES = {
    "spring": "Spring",
    "spr": "Spring",
    "summer": "Summer",
    "sum": "Summer",
    "fall": "Fall",
    "autumn": "Fall",
    "winter": "Winter",
}


@dataclass(frozen=True)
class CourseArchiveTarget:
    course_id: str
    shell_name: str
    year: str
    semester: str
    source_label: str


def select_recent_courses(
    courses: list[dict[str, Any]],
    years: int = 4,
    today: date | None = None,
    since_year: int | None = None,
) -> list[CourseArchiveTarget]:
    today = today or date.today()
    minimum_year = since_year if since_year is not None else today.year - years
    targets: list[CourseArchiveTarget] = []

    for course in courses:
        target = infer_archive_target(course)
        if int(target.year) >= minimum_year:
            targets.append(target)

    return sorted(targets, key=lambda item: (item.year, _semester_order(item.semester), item.shell_name))


def parse_number_selection(selection: str, total: int) -> list[int]:
    value = selection.strip().lower()
    if not value:
        return []
    if value == "all":
        return list(range(total))

    selected: set[int] = set()
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start = _selection_number(start_text, total)
            end = _selection_number(end_text, total)
            if start > end:
                start, end = end, start
            selected.update(range(start, end + 1))
        else:
            selected.add(_selection_number(token, total))

    return sorted(selected)


def infer_archive_target(course: dict[str, Any]) -> CourseArchiveTarget:
    course_id = str(course.get("id"))
    shell_name = str(course.get("name") or course.get("course_code") or f"course-{course_id}")
    term = course.get("term") if isinstance(course.get("term"), dict) else {}
    labels = [
        str(term.get("name") or ""),
        shell_name,
        str(course.get("course_code") or ""),
        str(course.get("sis_course_id") or ""),
    ]
    date_candidates = [
        str(term.get("start_at") or ""),
        str(term.get("end_at") or ""),
        str(course.get("start_at") or ""),
        str(course.get("end_at") or ""),
        str(course.get("created_at") or ""),
    ]

    parsed_date = next((_parse_canvas_date(value) for value in date_candidates if _parse_canvas_date(value)), None)
    year = parsed_date.year if parsed_date else _year_from_labels(labels)
    semester = _semester_from_labels(labels) or (semester_from_month(parsed_date.month) if parsed_date else "Unknown")

    return CourseArchiveTarget(
        course_id=course_id,
        shell_name=shell_name,
        year=str(year),
        semester=semester,
        source_label=str(term.get("name") or course.get("name") or course_id),
    )


def semester_from_month(month: int) -> str:
    if month in {1, 2, 3, 4, 5}:
        return "Spring"
    if month in {6, 7}:
        return "Summer"
    if month in {8, 9, 10, 11, 12}:
        return "Fall"
    return "Unknown"


def _parse_canvas_date(value: str) -> date | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        return None


def _semester_from_labels(labels: list[str]) -> str | None:
    text = " ".join(labels).lower()
    for alias, semester in SEMESTER_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", text):
            return semester
    return None


def _year_from_labels(labels: list[str]) -> int:
    text = " ".join(labels)
    matches = re.findall(r"\b(20\d{2})\b", text)
    if matches:
        return int(matches[0])
    return date.today().year


def _semester_order(semester: str) -> int:
    return {"Winter": 1, "Spring": 2, "Summer": 3, "Fall": 4}.get(semester, 9)


def _selection_number(value: str, total: int) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid selection value: {value!r}") from exc
    if number < 1 or number > total:
        raise ValueError(f"Selection {number} is outside the available range 1-{total}.")
    return number - 1
