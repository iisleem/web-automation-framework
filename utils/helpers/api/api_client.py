from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


@dataclass
class ApiResponse:
    status_code: int
    body: Any
    headers: dict
    text: str


class ApiClient:
    def __init__(
        self,
        base_url: str,
        default_headers: dict[str, str] | None = None,
        timeout_seconds: float = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.default_headers = default_headers or {}
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def get(self, path: str, **kwargs) -> ApiResponse:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> ApiResponse:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> ApiResponse:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> ApiResponse:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs) -> ApiResponse:
        headers = {**self.default_headers, **kwargs.pop("headers", {})}
        response = self.session.request(
            method,
            urljoin(self.base_url, path.lstrip("/")),
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout_seconds),
            **kwargs,
        )
        return _to_api_response(response)


def _to_api_response(response: requests.Response) -> ApiResponse:
    try:
        body = response.json()
    except ValueError:
        body = None
    return ApiResponse(
        status_code=response.status_code,
        body=body,
        headers=dict(response.headers),
        text=response.text,
    )
