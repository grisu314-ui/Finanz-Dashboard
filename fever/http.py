"""Central HTTP client: every outbound request of the project goes through here.

Host allowlist, HTTPS only, timeouts, retries with backoff, a minimum interval
per host (rate limits) and an own User-Agent. Failures raise FetchError with
secrets masked: requests and urllib3 put the full URL, including query
parameters such as the FRED api_key, into exception texts (tested 25.09.2026).
The retry loop is our own for the same reason: urllib3's Retry logs the URL.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlsplit

import requests

from fever import __version__
from fever.log import mask

# Host -> minimum seconds between two requests to it. Further hosts come with milestone M4.
ALLOWED_HOSTS = {
    "cdn.cboe.com": 1.0,
    "api.stlouisfed.org": 1.0,  # FRED allows 120 requests/minute per key (secondary sources)
}
USER_AGENT = f"Fieberthermometer/{__version__} (private, non-commercial)"
TIMEOUT = (10, 60)  # seconds: connect, read
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2, 4)  # wait before the 2nd and 3rd attempt
MAX_RETRY_AFTER = 60
MAX_REDIRECTS = 3
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})

logger = logging.getLogger(__name__)


class FetchError(RuntimeError):
    """Request failed or was refused; the message never contains secrets."""


@dataclass(frozen=True)
class Fetched:
    content: bytes
    retrieved_at: datetime
    status: int


class HttpClient:
    def __init__(self, session: requests.Session | None = None, *, sleep=time.sleep, clock=time.monotonic):
        self._session = session or requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT
        self._sleep = sleep
        self._clock = clock
        self._last_request: dict[str, float] = {}

    def get(self, url: str, params: dict | None = None) -> Fetched:
        """GET with retries on connection errors, timeouts, 429 and 5xx; only HTTP 200 counts."""
        try:
            shown = mask(requests.Request("GET", url, params=params).prepare().url)
        except requests.RequestException as exc:
            raise FetchError(f"Ungültige URL: {mask(str(exc))}") from None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = self._get_following_redirects(url, params)
            except requests.RequestException as exc:
                error = f"{type(exc).__name__}: {mask(str(exc))}"
                wait = BACKOFF_SECONDS[attempt - 1] if attempt < MAX_ATTEMPTS else 0
            else:
                if response.status_code == 200:
                    return Fetched(response.content, datetime.now(timezone.utc), 200)
                error = f"HTTP {response.status_code}"
                if response.status_code not in RETRY_STATUS:
                    raise FetchError(f"{shown}: {error}")
                backoff = BACKOFF_SECONDS[attempt - 1] if attempt < MAX_ATTEMPTS else 0
                wait = _retry_after(response) or backoff
            if attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Abruf fehlgeschlagen (%s), Versuch %d/%d, nächster in %.0f s: %s",
                    error, attempt, MAX_ATTEMPTS, wait, shown,
                )
                self._sleep(wait)
        raise FetchError(f"{shown}: {error} (nach {MAX_ATTEMPTS} Versuchen)")

    def _get_following_redirects(self, url: str, params: dict | None) -> requests.Response:
        for _ in range(MAX_REDIRECTS + 1):
            host = _check_url(url)
            self._throttle(host)
            response = self._session.get(url, params=params, timeout=TIMEOUT, allow_redirects=False)
            if not response.is_redirect:
                return response
            url = urljoin(response.url, response.headers["location"])
            params = None  # the redirect target carries its own query
        raise FetchError(f"Zu viele Weiterleitungen (> {MAX_REDIRECTS}): {mask(url)}")

    def _throttle(self, host: str) -> None:
        last = self._last_request.get(host)
        if last is not None:
            wait = ALLOWED_HOSTS[host] - (self._clock() - last)
            if wait > 0:
                self._sleep(wait)
        self._last_request[host] = self._clock()


def _check_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchError(f"Nur HTTPS erlaubt: {mask(url)}")
    if parts.hostname not in ALLOWED_HOSTS or parts.port not in (None, 443) or parts.username:
        raise FetchError(f"Host nicht auf der Allowlist: {mask(url)}")
    return parts.hostname


def _retry_after(response: requests.Response) -> float | None:
    """Seconds from a Retry-After header (seconds or HTTP date), capped; None if absent or invalid."""
    value = response.headers.get("retry-after")
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError):
            return None
    return min(max(seconds, 0.0), MAX_RETRY_AFTER)
