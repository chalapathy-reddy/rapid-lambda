from __future__ import annotations

import json
from typing import Any, Dict, Optional


class Response:
    def __init__(self, data: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.body = data
        self.status_code = status_code
        self.headers = headers or {}

        return {
            "statusCode": self.status_code,
            "headers": self.headers,
            "body": self.body,
        }


class JsonResponse(Response):
    def __init__(self, data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        body = json.dumps(data)
        headers = (headers.copy() if headers else {})
        headers.setdefault("Content-Type", "application/json")
        super().__init__(body, status_code=status_code, headers=headers)


class HtmlResponse(Response):
    def __init__(self, data: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        headers = (headers.copy() if headers else {})
        headers.setdefault("Content-Type", "text/html; charset=utf-8")
        super().__init__(data, status_code=status_code, headers=headers)


class TextResponse(Response):
    def __init__(self, data: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        headers = (headers.copy() if headers else {})
        headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        super().__init__(data, status_code=status_code, headers=headers)


class RedirectResponse(Response):
    def __init__(self, location: str, status_code: int = 302, headers: Optional[Dict[str, str]] = None):
        headers = (headers.copy() if headers else {})
        headers.setdefault("Location", location)
        super().__init__("", status_code=status_code, headers=headers)
