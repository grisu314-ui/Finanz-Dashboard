"""CFTC COT parser against a shortened real response (fetched 26.09.2026), request and group run."""

import json
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from sqlalchemy import select

from fever.config import group_members, series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, cftc
from fever.sources.update import update_group
from fever.store.db import make_engine
from fever.store.tables import observation

FIXTURE = Path(__file__).parent / "fixtures" / "cftc" / "6dca-aqww_1170E1.json"
CATALOG = series_catalog()
MEMBERS = group_members(CATALOG)["cftc_vx"]
AT = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


class RecordingClient:
    def __init__(self, content=b"[]"):
        self.content, self.calls = content, []

    def get(self, url, params=None):
        self.calls.append((url, params))
        return Fetched(self.content, AT, 200)


def body(*records):
    return json.dumps(list(records)).encode()


def record(day="2026-09-22", **values):
    return {"report_date_as_yyyy_mm_dd": f"{day}T00:00:00.000", **values}


def test_every_member_reads_its_own_field():
    content = FIXTURE.read_bytes()
    rows = {series.id: cftc.parse(content, series, AT) for series in MEMBERS}
    assert rows["cftc_vx_open_interest"][0] == Row(date(2004, 7, 27), 6450.0)
    assert rows["cftc_vx_noncomm_long"][-1] == Row(date(2026, 9, 22), 82776.0)
    assert rows["cftc_vx_noncomm_short"][-1] == Row(date(2026, 9, 22), 162056.0)
    assert rows["cftc_vx_noncomm_spread"][-1] == Row(date(2026, 9, 22), 90361.0)  # CFTC typo "postions"
    assert all(len(values) == 4 for values in rows.values())


def test_the_request_selects_the_market_and_the_fields():
    client = RecordingClient()
    cftc.fetch(client, CATALOG["cftc_vx_noncomm_short"])
    url, params = client.calls[0]
    assert url == "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
    assert params["$where"] == "cftc_contract_market_code='1170E1'"
    assert params["$select"] == (
        "report_date_as_yyyy_mm_dd,open_interest_all,noncomm_positions_long_all,"
        "noncomm_positions_short_all,noncomm_postions_spread_all"
    )
    assert params["$order"] == "report_date_as_yyyy_mm_dd" and params["$limit"] == "50000"
    assert urlsplit(url).hostname in ALLOWED_HOSTS


@pytest.mark.parametrize("source_id", ["1170E1", "1170E1/open_interest_other", "1170e1/open_interest_all", "1170E1' OR '1'='1/open_interest_all"])
def test_malformed_source_ids_are_errors(source_id):
    series = replace(CATALOG["cftc_vx_open_interest"], source_id=source_id)
    with pytest.raises(SourceError, match="ungültige Kennung"):
        cftc.fetch(RecordingClient(), series)


@pytest.mark.parametrize(
    "content, message",
    [
        (b"<html>Service Unavailable</html>", "keine gültige JSON-Antwort"),
        (b'{"error": true, "message": "query failed"}', "keine Liste"),
        (body({"open_interest_all": "1"}), "Eintrag 0: Stichtag fehlt"),
        (body(record(open_interest_all="12.5")), "Eintrag 0: unlesbar"),
        (body(record(day="22.09.2026", open_interest_all="1")), "Eintrag 0: unlesbar"),
        (body(record(open_interest_all=None)), "Eintrag 0: unlesbar"),
        (body(), "keine Werte"),
        (body(record(open_interest_all="1"), record(open_interest_all="2")), "Datum doppelt"),
    ],
)
def test_format_changes_are_errors(content, message):
    with pytest.raises(SourceError, match=message):
        cftc.parse(content, CATALOG["cftc_vx_open_interest"], AT)


def test_a_missing_field_is_a_missing_value():
    content = body(record("2026-09-15", open_interest_all="5"), record("2026-09-22"))
    assert cftc.parse(content, CATALOG["cftc_vx_open_interest"], AT) == [Row(date(2026, 9, 15), 5.0)]


def test_a_response_as_long_as_the_limit_may_be_truncated(monkeypatch):
    monkeypatch.setattr(cftc, "LIMIT", 2)
    content = body(record("2026-09-15", open_interest_all="5"), record("2026-09-22", open_interest_all="6"))
    with pytest.raises(SourceError, match="abgeschnitten"):
        cftc.parse(content, CATALOG["cftc_vx_open_interest"], AT)


def test_the_group_is_fetched_once_and_stored_with_estimated_friday_vintages(migrated_dir):
    engine = make_engine(migrated_dir)
    client = RecordingClient(FIXTURE.read_bytes())
    results = update_group(engine, migrated_dir, client, MEMBERS, clock=lambda: AT)
    assert len(client.calls) == 1 and [result.added for result in results] == [4] * 4
    assert len(list((migrated_dir / "raw" / "cftc" / "cftc_vx").glob("*.gz"))) == 1
    with engine.connect() as conn:
        last = conn.execute(
            select(observation).where(observation.c.series_id == "cftc_vx_noncomm_long").order_by(observation.c.obs_date.desc())
        ).first()
    # Tuesday 22.09.2026 + 3 days = Friday 25.09.2026, 15:45 EDT = 19:45 UTC (E-14)
    assert last.obs_date == date(2026, 9, 22) and last.value == 82776.0
    assert last.vintage == datetime(2026, 9, 25, 19, 45, tzinfo=timezone.utc) and last.vintage_estimated
