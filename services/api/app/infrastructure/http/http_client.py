from __future__ import annotations

import requests


class HttpClient:
    """
    Shared HTTP client for every external provider.

    Responsibilities:

    - Session reuse
    - Timeouts
    - Error handling

    Future:

    - Retries
    - Logging
    - Rate limiting
    - Caching
    """

    def __init__(self):
        self.session = requests.Session()

    def get(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int = 20,
    ):

        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()