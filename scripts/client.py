from typing import Any

import httpx

from scripts.config import XConfig


class XClient:
    """HTTP client for X API v2."""

    def __init__(self, config: XConfig | None = None, timeout: float = 30.0):
        self.config = config or XConfig.from_env()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.config.require_bearer_token()}"},
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._client.get(path, params=params or {})
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "XClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
