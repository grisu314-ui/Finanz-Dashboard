import logging

import pytest
import requests
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

from fever import log
from fever.http import BACKOFF_SECONDS, MAX_RETRY_AFTER, TIMEOUT, USER_AGENT, FetchError, HttpClient

KEY = "abcdef0123456789abcdef0123456789"
CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
FRED = "https://api.stlouisfed.org/fred/series/observations"


class FakeAdapter(BaseAdapter):
    """Plays back planned responses or exceptions instead of using the network."""

    def __init__(self, plan):
        super().__init__()
        self.plan = list(plan)
        self.sent = []

    def send(self, request, **kwargs):
        self.sent.append((request, kwargs))
        item = self.plan.pop(0)
        if isinstance(item, Exception):
            raise item
        status, headers, body = item
        response = requests.Response()
        response.status_code = status
        response.headers = CaseInsensitiveDict(headers)
        response._content = body
        response.url = request.url
        response.request = request
        return response

    def close(self):
        pass


class FakeTime:
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds

    def clock(self):
        return self.now


def client_for(plan):
    adapter = FakeAdapter(plan)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    fake = FakeTime()
    return HttpClient(session, sleep=fake.sleep, clock=fake.clock), adapter, fake


def test_success_returns_content_utc_time_and_sets_headers_and_timeouts():
    client, adapter, fake = client_for([(200, {}, b"DATE,CLOSE\n")])
    fetched = client.get(CBOE)
    assert fetched.content == b"DATE,CLOSE\n" and fetched.status == 200
    assert fetched.retrieved_at.utcoffset().total_seconds() == 0
    request, kwargs = adapter.sent[0]
    assert request.headers["User-Agent"] == USER_AGENT
    assert kwargs["timeout"] == TIMEOUT and kwargs["verify"] is True
    assert fake.sleeps == []


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org/data.csv",
        "http://cdn.cboe.com/api/x.csv",
        "https://cdn.cboe.com:8443/api/x.csv",
        "https://user@cdn.cboe.com/api/x.csv",
        "https://cdn.cboe.com.example.org/x.csv",
    ],
)
def test_refuses_urls_outside_the_allowlist_without_sending(url):
    client, adapter, _ = client_for([])
    with pytest.raises(FetchError):
        client.get(url)
    assert adapter.sent == []


def test_follows_redirects_within_the_allowlist():
    client, adapter, _ = client_for([(302, {"Location": "/api/moved.csv"}, b""), (200, {}, b"ok")])
    assert client.get(CBOE).content == b"ok"
    assert adapter.sent[1][0].url == "https://cdn.cboe.com/api/moved.csv"


def test_refuses_redirect_to_a_foreign_host():
    client, adapter, _ = client_for([(301, {"Location": "https://evil.example/x"}, b"")])
    with pytest.raises(FetchError, match="Allowlist"):
        client.get(CBOE)
    assert len(adapter.sent) == 1


def test_stops_after_too_many_redirects():
    client, _, _ = client_for([(302, {"Location": CBOE}, b"")] * 4)
    with pytest.raises(FetchError, match="Zu viele Weiterleitungen"):
        client.get(CBOE)


def test_retries_server_errors_with_backoff_then_succeeds():
    client, adapter, fake = client_for([(503, {}, b""), (502, {}, b""), (200, {}, b"ok")])
    assert client.get(CBOE).content == b"ok"
    assert fake.sleeps == list(BACKOFF_SECONDS) and len(adapter.sent) == 3


def test_retry_after_is_honoured_and_capped():
    client, _, fake = client_for([(429, {"Retry-After": "5"}, b""), (429, {"Retry-After": "3600"}, b""), (200, {}, b"")])
    client.get(FRED)
    assert fake.sleeps == [5.0, MAX_RETRY_AFTER]


def test_gives_up_after_three_connection_errors():
    errors = [requests.ConnectionError("connection refused")] * 3
    client, adapter, fake = client_for(errors)
    with pytest.raises(FetchError, match="ConnectionError.*nach 3 Versuchen"):
        client.get(CBOE)
    assert len(adapter.sent) == 3 and fake.sleeps == list(BACKOFF_SECONDS)


def test_timeouts_are_retried():
    client, _, _ = client_for([requests.Timeout("read timed out"), (200, {}, b"ok")])
    assert client.get(CBOE).content == b"ok"


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_client_errors_are_not_retried(status):
    client, adapter, fake = client_for([(status, {}, b"")])
    with pytest.raises(FetchError, match=f"HTTP {status}"):
        client.get(CBOE)
    assert len(adapter.sent) == 1 and fake.sleeps == []


def test_minimum_interval_per_host():
    client, _, fake = client_for([(200, {}, b"")] * 3)
    client.get(CBOE)
    client.get(CBOE)
    client.get(FRED)
    assert fake.sleeps == [1.0]


def test_api_key_never_appears_in_errors_or_logs(monkeypatch, capsys):
    monkeypatch.setenv("FRED_API_KEY", KEY)
    log.setup()
    leaking = requests.ConnectionError(f"Max retries exceeded with url: /fred/series/observations?api_key={KEY}")
    client, adapter, _ = client_for([leaking, (503, {}, b""), (503, {}, b"")])
    with pytest.raises(FetchError) as info:
        client.get(FRED, params={"series_id": "NFCI", "api_key": KEY})
    assert KEY in adapter.sent[0][0].url  # the key is really sent ...
    assert KEY not in str(info.value) and "api_key=***" in str(info.value)  # ... but never shown

    logging.getLogger("urllib3.connectionpool").warning("Retrying after error: %s", f"/fred?api_key={KEY}")
    try:
        raise requests.HTTPError(f"403 Client Error for url: {FRED}?api_key={KEY}")
    except requests.HTTPError:
        logging.getLogger("fever.worker").exception("Abruf fehlgeschlagen")
    out = capsys.readouterr().out
    assert KEY not in out and out.count("***") >= 3


def test_invalid_url_is_a_fetch_error_without_secret(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", KEY)
    client, _, _ = client_for([])
    with pytest.raises(FetchError, match="Ungültige URL") as info:
        client.get(f"not a url {KEY}")
    assert KEY not in str(info.value)


def test_mask_leaves_text_alone_without_secret(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    assert log.mask("api_key=abc") == "api_key=abc"
