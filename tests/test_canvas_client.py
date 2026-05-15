from canvas_download.canvas_client import _next_link


def test_next_link_parses_canvas_link_header() -> None:
    header = (
        '<https://school.instructure.com/api/v1/courses?page=1>; rel="current", '
        '<https://school.instructure.com/api/v1/courses?page=2>; rel="next", '
        '<https://school.instructure.com/api/v1/courses?page=4>; rel="last"'
    )

    assert _next_link(header) == "https://school.instructure.com/api/v1/courses?page=2"


def test_next_link_returns_none_without_next_relation() -> None:
    assert _next_link('<https://school.instructure.com/api/v1/courses?page=1>; rel="current"') is None
