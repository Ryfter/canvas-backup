from __future__ import annotations

from collections.abc import Iterator
import time
from typing import Any
from urllib.parse import urljoin

import requests


class CanvasApiError(RuntimeError):
    pass


class CanvasClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        session: requests.Session | None = None,
        timeout: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
        )

    def list_courses(self) -> list[dict[str, Any]]:
        return list(
            self.paginated_get(
                "/api/v1/courses",
                params={
                    "include[]": ["term", "sections", "concluded"],
                    "state[]": ["unpublished", "available", "completed"],
                },
            )
        )

    def get_course(self, course_id: int | str) -> dict[str, Any]:
        return self.get(f"/api/v1/courses/{course_id}", params={"include[]": ["term", "sections"]})

    def list_folders(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/courses/{course_id}/folders"))

    def list_files(self, folder_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/folders/{folder_id}/files"))

    def list_modules(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/courses/{course_id}/modules"))

    def list_module_items(self, course_id: int | str, module_id: int | str) -> list[dict[str, Any]]:
        return list(
            self.paginated_get(
                f"/api/v1/courses/{course_id}/modules/{module_id}/items",
                params={"include[]": ["content_details"]},
            )
        )

    def list_pages(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/courses/{course_id}/pages"))

    def get_page(self, course_id: int | str, page_url: str) -> dict[str, Any]:
        return self.get(f"/api/v1/courses/{course_id}/pages/{page_url}")

    def list_assignments(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(
            self.paginated_get(
                f"/api/v1/courses/{course_id}/assignments",
                params={"include[]": ["all_dates", "overrides", "rubric"]},
            )
        )

    def effective_due_dates(self, course_id: int | str) -> dict[str, Any]:
        return self.get(f"/api/v1/courses/{course_id}/effective_due_dates")

    def list_quizzes(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/courses/{course_id}/quizzes"))

    def list_discussion_topics(self, course_id: int | str) -> list[dict[str, Any]]:
        return list(self.paginated_get(f"/api/v1/courses/{course_id}/discussion_topics"))

    def get(self, path_or_url: str, params: dict[str, Any] | None = None) -> Any:
        response = self._request("GET", path_or_url, params=params)
        return response.json()

    def paginated_get(
        self, path_or_url: str, params: dict[str, Any] | None = None
    ) -> Iterator[dict[str, Any]]:
        next_url: str | None = path_or_url
        next_params = {"per_page": 100, **(params or {})}
        while next_url:
            response = self._request("GET", next_url, params=next_params)
            payload = response.json()
            if isinstance(payload, list):
                yield from payload
            else:
                raise CanvasApiError(f"Expected list response from {next_url}, got {type(payload).__name__}")
            next_url = _next_link(response.headers.get("Link", ""))
            next_params = None

    def download_file(self, url: str, target_path: str) -> None:
        response = self._request("GET", url, stream=True)
        with open(target_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)

    def _request(self, method: str, path_or_url: str, **kwargs: Any) -> requests.Response:
        url = path_or_url if path_or_url.startswith("http") else urljoin(self.base_url, path_or_url.lstrip("/"))
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
                    time.sleep(2**attempt)
                    continue
                if response.status_code >= 400:
                    raise CanvasApiError(f"Canvas API {response.status_code} for {method} {url}: {response.text}")
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 3:
                    time.sleep(2**attempt)
                    continue
                raise CanvasApiError(f"Canvas request failed for {method} {url}: {exc}") from exc
        raise CanvasApiError(f"Canvas request failed for {method} {url}: {last_error}")


def _next_link(header: str) -> str | None:
    for part in header.split(","):
        section = part.strip()
        if 'rel="next"' not in section:
            continue
        if section.startswith("<") and ">" in section:
            return section[1 : section.index(">")]
    return None
