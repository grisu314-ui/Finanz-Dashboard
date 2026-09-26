"""VX futures term structure by rank (E-45, E-46) with synthetic settlements (E-27)."""

import json
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from sqlalchemy import select

from fever.config import group_members, series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, cfe
from fever.sources.update import estimated_release, update_group
from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations
from fever.store.tables import observation

FIXTURES = Path(__file__).parent / "fixtures" / "cfe"
LISTING = (FIXTURES / "product_list_VX.json").read_bytes()
CATALOG = series_catalog()
MEMBERS = group_members(CATALOG)["cfe_vx"]
# Saturday 26.09.2026, 12:00 UTC: Friday 25.09. is settled
AT = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
FRIDAY = date(2026, 9, 25)
# the monthly expiries of the fixture list
EXPIRIES = [date(2026, 8, 19), date(2026, 9, 16), date(2026, 10, 21), date(2026, 11, 18), date(2026, 12, 16),
            date(2027, 1, 20), date(2027, 2, 17), date(2027, 3, 17), date(2027, 4, 21), date(2027, 5, 18),
            date(2027, 6, 16)]


def contract(expiry, rows):
    """A contract file in Cboe's format; rows: (trading day, settlement)."""
    lines = [",".join(cfe.HEADER)]
    for day, settle in rows:
        lines.append(f"{day},X ({expiry:%b %Y}),1.0,1.0,1.0,1.0,{settle},0,10,0,100")
    return "\n".join(lines) + "\n"


def bundle(files, from_date=None):
    contracts = {expiry.isoformat(): text for expiry, text in files.items()}
    return json.dumps({"from_date": from_date and from_date.isoformat(), "contracts": contracts}).encode()


def curve(days, *, skip=(), zero=()):
    """Every fixture contract with a row on each day (listed from 01.01.2026); settle = 10 + index."""
    files = {}
    for index, expiry in enumerate(EXPIRIES):
        rows = [(date(2026, 1, 1), 1.0)]
        rows += [(day, 0 if (expiry, day) in zero else 10 + index) for day in days if day <= expiry and (expiry, day) not in skip]
        files[expiry] = contract(expiry, rows)
    return files


def values(content, series_id, at=AT):
    return {row.obs_date: row.value for row in cfe.parse(content, CATALOG[series_id], at)}


def test_ranks_are_the_running_monthly_contracts_in_expiry_order():
    content = bundle(curve([FRIDAY]))
    assert values(content, "cfe_vx1")[FRIDAY] == 12  # Oct 2026: August and September have expired
    assert values(content, "cfe_vx1_days")[FRIDAY] == 26  # 25.09. -> 21.10.
    assert values(content, "cfe_vx8")[FRIDAY] == 19  # May 2027
    assert values(content, "cfe_vx8_days")[FRIDAY] == (date(2027, 5, 18) - FRIDAY).days


def test_the_expiring_contract_no_longer_counts_on_its_expiry_day():
    expiry_day = date(2026, 9, 16)
    content = bundle(curve([expiry_day - timedelta(days=1), expiry_day]))
    assert values(content, "cfe_vx1")[expiry_day - timedelta(days=1)] == 11  # September contract
    assert values(content, "cfe_vx1")[expiry_day] == 12  # already October
    assert values(content, "cfe_vx1_days")[expiry_day] == 35


def test_a_missing_row_leaves_its_rank_empty_and_later_ranks_do_not_move_up():
    content = bundle(curve([FRIDAY], skip={(date(2026, 11, 18), FRIDAY)}))
    assert FRIDAY not in values(content, "cfe_vx2") and FRIDAY not in values(content, "cfe_vx2_days")
    assert values(content, "cfe_vx3")[FRIDAY] == 14  # still December


def test_settlement_zero_is_a_missing_value():
    content = bundle(curve([FRIDAY], zero={(date(2026, 10, 21), FRIDAY)}))
    assert FRIDAY not in values(content, "cfe_vx1")
    assert values(content, "cfe_vx2")[FRIDAY] == 13


def test_a_contract_counts_only_from_its_first_row():
    files = curve([FRIDAY])
    files[date(2027, 6, 16)] = contract(date(2027, 6, 16), [(date(2026, 9, 25), 30.0)])
    files[date(2027, 5, 18)] = contract(date(2027, 5, 18), [(date(2026, 9, 28), 29.0)])  # listed later
    day = values(bundle(files), "cfe_vx8")
    assert day[FRIDAY] == 30.0  # June takes rank 8 because May was not listed yet


def test_days_before_from_date_are_left_out():
    content = bundle(curve([date(2026, 9, 1), FRIDAY]), from_date=date(2026, 9, 2))
    assert list(values(content, "cfe_vx1")) == [FRIDAY]


def test_the_running_day_counts_only_from_release_time():
    content = bundle(curve([FRIDAY]))
    before = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)  # 16:00 New York
    after = datetime(2026, 9, 26, 2, 0, tzinfo=timezone.utc)  # 22:00 New York
    assert FRIDAY not in values(content, "cfe_vx1", before)
    assert FRIDAY in values(content, "cfe_vx1", after)


def test_the_real_file_format_is_read():
    files = curve([FRIDAY])
    files[date(2026, 10, 21)] = (FIXTURES / "VX_2026-10-21.csv").read_text()
    september = {day: value for day, value in values(bundle(files), "cfe_vx1").items() if day.month == 9}
    assert september == {date(2026, 9, 24): 18.1234, FRIDAY: 18.01}


@pytest.mark.parametrize(
    "text, message",
    [
        ("Date,Futures,Settle\n2026-09-25,V (Oct 2026),18\n", "unerwartete Kopfzeile"),
        (contract(date(2026, 11, 18), [(FRIDAY, 18.0)]), "passt nicht zum Verfall"),
        (contract(date(2026, 10, 21), [(date(2026, 10, 22), 18.0)]), "nach dem Verfall oder doppelt"),
        (contract(date(2026, 10, 21), [(FRIDAY, 18.0), (FRIDAY, 18.1)]), "nach dem Verfall oder doppelt"),
        (contract(date(2026, 10, 21), [(FRIDAY, "n/a")]), "unlesbar"),
        (contract(date(2026, 10, 21), [(FRIDAY, 18.0)]).replace(",100\n", "\n"), "10 statt 11 Felder"),
    ],
)
def test_format_changes_in_a_contract_file_are_errors(text, message):
    files = curve([FRIDAY])
    files[date(2026, 10, 21)] = text
    with pytest.raises(SourceError, match=message):
        cfe.parse(bundle(files), CATALOG["cfe_vx1"], AT)


@pytest.mark.parametrize("content", [b"<html>", b'{"contracts": {}}', b'{"from_date": null, "contracts": {"2026-13-01": ""}}'])
def test_a_broken_bundle_is_an_error(content):
    with pytest.raises(SourceError, match="Abrufbündel unlesbar"):
        cfe.parse(content, CATALOG["cfe_vx1"], AT)


@pytest.mark.parametrize("source_id", ["VX9", "VX0", "VX1_days", "VX", "VX10"])
def test_malformed_source_ids_are_errors(source_id):
    with pytest.raises(SourceError, match="ungültige Kennung"):
        cfe.parse(bundle(curve([FRIDAY])), replace(CATALOG["cfe_vx1"], source_id=source_id), AT)


# --- contract list and fetch ---------------------------------------------------------------------


class Client:
    """Serves the fixture list and one synthetic row per contract, on `day` or its expiry if earlier."""

    def __init__(self, listing=LISTING, day=FRIDAY, at=AT):
        self.listing, self.day, self.at, self.urls = listing, day, at, []

    def get(self, url, params=None):
        self.urls.append(url)
        if url == cfe.LIST_URL:
            return Fetched(self.listing, self.at, 200)
        expiry = date.fromisoformat(url[-14:-4])
        return Fetched(contract(expiry, [(min(expiry, self.day), 20.0)]).encode(), self.at + timedelta(seconds=len(self.urls)), 200)


def test_the_list_yields_monthly_contracts_only():
    contracts = cfe._monthly_contracts(LISTING, FRIDAY)
    assert sorted(contracts) == EXPIRIES  # the weeklies of 30.09. and 07.10. are left out


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda d: d["2027"].clear(), "nur 3 laufende Monatskontrakte"),
        (lambda d: d["2026"][2].update(expire_date="2026-10-22"), "unerwarteter Eintrag"),
        (lambda d: d["2026"].append(dict(d["2026"][2], path=d["2026"][2]["path"].replace("VX/VX_", "VX/old/VX_"))), "unerwarteter Eintrag"),
        (lambda d: d.update({"2026": "x"}), "nicht die Form"),
    ],
)
def test_contract_list_changes_are_errors(change, message):
    data = json.loads(LISTING)
    change(data)
    with pytest.raises(SourceError, match=message):
        cfe._monthly_contracts(json.dumps(data).encode(), FRIDAY)


def test_first_fetch_loads_every_monthly_contract_later_ones_only_the_window():
    client = Client()
    fetched = cfe.fetch(client, CATALOG["cfe_vx1"])
    assert len(client.urls) == 1 + len(EXPIRIES)
    assert all(urlsplit(url).hostname in ALLOWED_HOSTS for url in client.urls)
    assert json.loads(fetched.content)["from_date"] is None
    assert fetched.retrieved_at == AT + timedelta(seconds=len(client.urls))  # time of the last file

    client = Client()
    fetched = cfe.fetch(client, CATALOG["cfe_vx1"], since=FRIDAY)  # window starts 11.08.2026
    assert len(client.urls) == 1 + len(EXPIRIES)  # August 2026 is the oldest fixture contract
    client = Client()
    fetched = cfe.fetch(client, CATALOG["cfe_vx1"], since=date(2026, 10, 5))  # window starts 21.08.2026
    assert [url[-14:-4] for url in client.urls[1:3]] == ["2026-09-16", "2026-10-21"]
    assert json.loads(fetched.content)["from_date"] == "2026-08-21"


def test_the_group_uses_the_newest_stored_day_as_since(migrated_dir):
    engine = make_engine(migrated_dir)
    client = Client()
    first = update_group(engine, migrated_dir, client, MEMBERS, clock=lambda: AT)
    assert [result.added for result in first] == [1] * 16 and len(client.urls) == 12
    with engine.connect() as conn:
        row = conn.execute(select(observation).where(observation.c.series_id == "cfe_vx1_days")).one()
    assert (row.obs_date, row.value) == (FRIDAY, 26.0)

    later = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
    client = Client(day=date(2026, 10, 6), at=later)
    assert all(result.added == 1 for result in update_group(engine, migrated_dir, client, MEMBERS, clock=lambda: later))
    assert client.urls[1].endswith("VX_2026-08-19.csv")  # since 25.09. -> window from 11.08.
    client = Client(day=date(2026, 10, 6), at=later)
    update_group(engine, migrated_dir, client, MEMBERS, clock=lambda: later)
    assert client.urls[1].endswith("VX_2026-09-16.csv")  # since 06.10. -> window from 22.08.


def test_since_is_the_oldest_newest_day_of_the_members(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:  # every member stored up to 06.10., one only up to 25.09.
        for series in MEMBERS:
            day = FRIDAY if series.id == "cfe_vx8" else date(2026, 10, 6)
            append_observations(conn, series.id, [NewObservation(day, 20.0, AT, False)], retrieved_at=AT)
    later = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)
    client = Client(day=date(2026, 10, 6), at=later)
    update_group(engine, migrated_dir, client, MEMBERS, clock=lambda: later)
    assert client.urls[1].endswith("VX_2026-08-19.csv")  # window from 11.08., not from 22.08.


def test_estimated_release_is_the_trading_day_at_22_new_york():
    assert estimated_release(FRIDAY, CATALOG["cfe_vx3"]) == datetime(2026, 9, 26, 2, 0, tzinfo=timezone.utc)
