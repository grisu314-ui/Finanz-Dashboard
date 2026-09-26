import json
import logging
from dataclasses import replace
from datetime import date, datetime, time, timezone
from pathlib import Path

import pytest
import requests
from requests.adapters import BaseAdapter
from sqlalchemy import select

from fever.config import series_catalog
from fever.http import FetchError, Fetched, HttpClient
from fever.sources.update import UpdateResult, estimated_release, update_series
from fever.store.db import make_engine
from fever.store.observations import latest_values
from fever.store.status import read_status
from fever.store.tables import observation

FIXTURES = Path(__file__).parent / "fixtures"
CATALOG = series_catalog()
HY = CATALOG["bamlh0a0hym2"]
UTC = timezone.utc
KEY = "0123456789abcdef0123456789abcdef"
# Friday 25.09.2026, 10:30 New York (EDT): Thursday's ICE values are out (release 10:15).
FIRST = datetime(2026, 9, 25, 14, 30, tzinfo=UTC)
NEXT_DAY = datetime(2026, 9, 26, 14, 30, tzinfo=UTC)


class FakeClient:
    def __init__(self, *items):
        self.items = list(items)

    def get(self, url, params=None):
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def fred_key(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", KEY)


@pytest.fixture
def engine(migrated_dir):
    return make_engine(migrated_dir)


def hy_json(change=None):
    data = json.loads((FIXTURES / "fred" / "BAMLH0A0HYM2.json").read_bytes())
    if change:
        change(data["observations"])
        data["count"] = len(data["observations"])
    return json.dumps(data).encode()


def run(engine, data_dir, series, content_or_error, at):
    item = content_or_error if isinstance(content_or_error, Exception) else Fetched(content_or_error, at, 200)
    return update_series(engine, data_dir, FakeClient(item), series, clock=lambda: at)


def stored(engine, series_id):
    with engine.connect() as conn:
        query = (
            select(observation)
            .where(observation.c.series_id == series_id)
            .order_by(observation.c.obs_date, observation.c.vintage)
        )
        return conn.execute(query).all()


def status(engine, source):
    with engine.connect() as conn:
        return next(row for row in read_status(conn) if row["source"] == source)


def raw_files(data_dir, source, series_id):
    return sorted((data_dir / "raw" / source / series_id).glob("*.gz"))


@pytest.mark.parametrize(
    "obs_date, lag_days, release, expected",
    [
        (date(2026, 3, 5), 1, time(16, 30), datetime(2026, 3, 6, 21, 30, tzinfo=UTC)),  # Thu -> Fri, EST
        (date(2026, 3, 6), 1, time(16, 30), datetime(2026, 3, 9, 20, 30, tzinfo=UTC)),  # Sat -> Mon, EDT from 08.03.
        (date(2026, 10, 30), 1, time(16, 30), datetime(2026, 11, 2, 21, 30, tzinfo=UTC)),  # Sat -> Mon, EST from 01.11.
        (date(2026, 8, 1), 37, time(10, 0), datetime(2026, 9, 7, 14, 0, tzinfo=UTC)),  # monthly, Monday
        (date(2026, 9, 26), 0, time(22, 0), datetime(2026, 9, 29, 2, 0, tzinfo=UTC)),  # Sat -> Mon 22:00 EDT
    ],
)
def test_estimated_release_moves_weekends_to_monday_and_converts_new_york_time(obs_date, lag_days, release, expected):
    series = replace(HY, lag_days=lag_days, release_time=release)
    assert estimated_release(obs_date, series) == expected


def test_first_fetch_stores_estimated_vintages(engine, migrated_dir):
    result = run(engine, migrated_dir, HY, hy_json(), FIRST)
    assert result == UpdateResult(added=10, rejected=0, error=None)

    rows = {row.obs_date: row for row in stored(engine, HY.id)}
    assert date(2025, 12, 25) not in rows  # "." is skipped, never stored
    assert all(row.vintage_estimated and row.retrieved_at == FIRST for row in rows.values())
    # lag 1 day, 10:15 New York; Saturday/Sunday -> Monday (E-14)
    assert rows[date(2026, 9, 23)].vintage == datetime(2026, 9, 24, 14, 15, tzinfo=UTC)  # Wed -> Thu, EDT
    assert rows[date(2025, 12, 26)].vintage == datetime(2025, 12, 29, 15, 15, tzinfo=UTC)  # Fri -> Mon, EST
    assert rows[date(2026, 5, 29)].vintage == datetime(2026, 6, 1, 14, 15, tzinfo=UTC)  # Fri -> Mon
    assert rows[date(2026, 5, 31)].vintage == datetime(2026, 6, 1, 14, 15, tzinfo=UTC)  # Sun month end -> Mon
    assert rows[date(2026, 9, 24)].vintage == datetime(2026, 9, 25, 14, 15, tzinfo=UTC)

    record = status(engine, "fred")
    assert record["last_success_at"] == FIRST and record["last_error_at"] is None


def test_estimated_vintage_is_never_later_than_the_retrieval(engine, migrated_dir):
    early = datetime(2026, 9, 25, 14, 0, tzinfo=UTC)  # 10:00 New York, before the usual 10:15
    run(engine, migrated_dir, HY, hy_json(), early)
    last = stored(engine, HY.id)[-1]
    assert last.obs_date == date(2026, 9, 24)
    assert last.vintage == early and last.vintage_estimated


def test_identical_second_fetch_adds_no_row_and_no_raw_file(engine, migrated_dir):
    run(engine, migrated_dir, HY, hy_json(), FIRST)
    result = run(engine, migrated_dir, HY, hy_json(), NEXT_DAY)
    assert result == UpdateResult(added=0, rejected=0, error=None)
    assert len(stored(engine, HY.id)) == 10
    assert len(raw_files(migrated_dir, "fred", HY.id)) == 1


def test_later_fetch_stores_new_and_revised_values_with_the_retrieval_time(engine, migrated_dir):
    run(engine, migrated_dir, HY, hy_json(), FIRST)

    def revise_and_extend(observations):
        observations[-1]["value"] = "2.81"
        observations.append({"realtime_start": "2026-09-26", "realtime_end": "2026-09-26", "date": "2026-09-25", "value": "2.75"})

    result = run(engine, migrated_dir, HY, hy_json(revise_and_extend), NEXT_DAY)
    assert result.added == 2

    revised = [row for row in stored(engine, HY.id) if row.obs_date == date(2026, 9, 24)]
    assert [(row.value, row.vintage_estimated) for row in revised] == [(3.09, True), (2.81, False)]
    assert revised[1].vintage == NEXT_DAY
    new = [row for row in stored(engine, HY.id) if row.obs_date == date(2026, 9, 25)]
    assert [(row.value, row.vintage, row.vintage_estimated) for row in new] == [(2.75, NEXT_DAY, False)]
    with engine.connect() as conn:
        assert latest_values(conn, HY.id)[-2].value == 2.81


def test_value_outside_the_bounds_is_dropped_rest_is_stored_and_reported(engine, migrated_dir, caplog):
    def unit_error(observations):
        next(o for o in observations if o["date"] == "2026-09-23")["value"] = "273"  # basis points

    with caplog.at_level(logging.ERROR):
        result = run(engine, migrated_dir, HY, hy_json(unit_error), FIRST)

    expected = "bamlh0a0hym2: 1 Wert(e) verworfen: 23.09.2026: Wert 273 außerhalb der Grenzen [0; 50]"
    assert result == UpdateResult(added=9, rejected=1, error=expected)
    assert date(2026, 9, 23) not in {row.obs_date for row in stored(engine, HY.id)}
    record = status(engine, "fred")
    assert record["last_error_message"] == expected
    assert record["last_error_at"] == FIRST and record["last_success_at"] == FIRST
    assert expected in caplog.text


def test_many_problems_are_summarised(engine, migrated_dir):
    def all_wrong(observations):
        for o in observations:
            if o["value"] != ".":
                o["value"] = "-1"

    result = run(engine, migrated_dir, HY, hy_json(all_wrong), FIRST)
    assert result.added == 0 and result.rejected == 10
    assert result.error.endswith("(und 5 weitere)")


def test_iorb_may_be_dated_up_to_lead_days_ahead(engine, migrated_dir):
    iorb = CATALOG["iorb"]
    at = datetime(2026, 9, 25, 15, 0, tzinfo=UTC)  # Friday 11:00 New York; FRED lists up to Monday 28.09.
    result = run(engine, migrated_dir, iorb, (FIXTURES / "fred" / "IORB.json").read_bytes(), at)
    assert result == UpdateResult(added=5, rejected=0, error=None)
    monday = stored(engine, "iorb")[-1]
    assert monday.obs_date == date(2026, 9, 28) and monday.vintage == at  # estimate capped at retrieval


def test_future_dates_are_rejected_without_lead_days(engine, migrated_dir):
    iorb = replace(CATALOG["iorb"], lead_days=0)
    at = datetime(2026, 9, 25, 15, 0, tzinfo=UTC)
    result = run(engine, migrated_dir, iorb, (FIXTURES / "fred" / "IORB.json").read_bytes(), at)
    assert result.added == 2 and result.rejected == 3
    assert "26.09.2026: Datum liegt in der Zukunft" in result.error


def test_rows_before_start_are_skipped_without_error(engine, migrated_dir):
    at = datetime(2026, 9, 26, 12, 0, tzinfo=UTC)
    result = run(engine, migrated_dir, CATALOG["vvix"], (FIXTURES / "cboe" / "VVIX_History.csv").read_bytes(), at)
    assert result == UpdateResult(added=4, rejected=0, error=None)
    rows = stored(engine, "vvix")
    assert rows[0].obs_date == date(2007, 1, 3)
    # Friday close, lag 0, 22:00 New York (EDT) = Saturday 02:00 UTC
    assert rows[-1].vintage == datetime(2026, 9, 26, 2, 0, tzinfo=UTC)


def test_fetch_error_is_recorded_and_nothing_is_stored(engine, migrated_dir, caplog):
    error = FetchError("https://api.stlouisfed.org/fred/series/observations?api_key=***: HTTP 503 (nach 3 Versuchen)")
    with caplog.at_level(logging.ERROR):
        result = run(engine, migrated_dir, HY, error, FIRST)
    assert result.added == 0 and result.error.startswith("bamlh0a0hym2: https://api.stlouisfed.org")
    assert stored(engine, HY.id) == []
    record = status(engine, "fred")
    assert record["last_attempt_at"] == FIRST and record["last_success_at"] is None
    assert record["last_error_message"] == result.error
    assert "HTTP 503" in caplog.text


def test_format_change_is_recorded_nothing_stored_but_raw_response_kept(engine, migrated_dir):
    result = run(engine, migrated_dir, HY, b"<html>Service moved</html>", FIRST)
    assert result.error == "bamlh0a0hym2: keine gültige JSON-Antwort"
    assert stored(engine, HY.id) == []
    assert len(raw_files(migrated_dir, "fred", HY.id)) == 1


class FailingAdapter(BaseAdapter):
    """requests puts the full URL, api_key included, into its exception text."""

    def send(self, request, **kwargs):
        raise requests.ConnectionError(f"cannot connect: {request.url}")

    def close(self):
        pass


def test_api_key_appears_neither_in_logs_nor_in_the_status(engine, migrated_dir, caplog):
    session = requests.Session()
    session.mount("https://", FailingAdapter())
    client = HttpClient(session, sleep=lambda seconds: None)
    with caplog.at_level(logging.DEBUG):
        result = update_series(engine, migrated_dir, client, HY, clock=lambda: FIRST)
    assert "api_key=***" in result.error
    assert KEY not in result.error
    assert KEY not in caplog.text
    assert KEY not in status(engine, "fred")["last_error_message"]
