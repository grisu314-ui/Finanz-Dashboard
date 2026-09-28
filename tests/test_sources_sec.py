"""SEC EDGAR N-PORT: top-10 concentration of the SPDR S&P 500 ETF Trust (E-71, E-74).

The fixtures are real, shortened SEC documents (public information, tests/fixtures/README.md):
the submissions list with two N-PORT filings and three others, and the filing for 30.06.2026 with
its 14 largest common stock positions, one position without LEI and one rights position.
"""

import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from sqlalchemy import select

from fever.config import series_catalog
from fever.http import ALLOWED_HOSTS, USER_AGENT, Fetched
from fever.sources import SourceError, sec
from fever.sources.update import update_series
from fever.store.db import make_engine
from fever.store.tables import observation

FIXTURES = Path(__file__).parent / "fixtures" / "sec"
SUBMISSIONS = (FIXTURES / "CIK0000884394.json").read_bytes()
XML = (FIXTURES / "nport_2026-06-30.xml").read_text(encoding="utf-8")
SERIES = series_catalog()["sec_spy_top10"]
AT = datetime(2026, 9, 28, 22, 30, tzinfo=timezone.utc)
CONTACT = "Max Mustermann max@example.org"


@pytest.fixture(autouse=True)
def contact(monkeypatch):
    monkeypatch.setenv("FEVER_SEC_CONTACT", CONTACT)


@pytest.fixture
def few_positions(monkeypatch):
    """The fixture filing is cut to 16 positions; the real ones hold about 500."""
    monkeypatch.setattr(sec, "MIN_POSITIONS", 10)


def bundle(*filings):
    return json.dumps({"since": None, "filings": list(filings)}).encode()


def filing(report_date="2026-06-30", xml=XML, accession="0001410368-26-089410"):
    return {"accession": accession, "filing_date": "2026-08-28", "report_date": report_date, "document": "primary_doc.xml",
            "form": "NPORT-P", "xml": xml}


def test_top_share_adds_share_classes_of_one_issuer_and_groups_missing_leis_by_name():
    lei_a, lei_b = "A" * 20, "B" * 20
    positions = [(lei_a, "Alpha A", 3.0), (lei_a, "Alpha C", 2.5), (lei_b, "Beta", 5.0),
                 ("N/A", "Gamma Corp", 1.0), ("N/A", "gamma corp ", 1.5), ("N/A", "Delta", 2.0)]
    # issuers: Alpha 5.5, Beta 5.0, Gamma 2.5, Delta 2.0
    assert sec.top_share(positions, top=2) == pytest.approx(10.5)
    assert sec.top_share(positions, top=3) == pytest.approx(13.0)
    assert sec.top_share(positions, top=10) == pytest.approx(15.0)


def test_parse_counts_the_ten_largest_issuers_of_the_real_filing(few_positions):
    rows = sec.parse(bundle(filing()), SERIES, AT)
    assert [row.obs_date for row in rows] == [date(2026, 6, 30)]
    # NVIDIA, Apple, Microsoft, Amazon, Alphabet (two share classes), Broadcom, Micron, Meta, Tesla, Eli Lilly
    assert rows[0].value == pytest.approx(7.517 + 6.592 + 4.298 + 3.619 + (3.250 + 2.590) + 2.774 + 2.019 + 1.919 + 1.837 + 1.472, abs=0.002)


def test_parse_ignores_rights_and_short_positions(few_positions):
    xml = XML.replace("<assetCat>EC</assetCat>", "<assetCat>DE</assetCat>", 1)  # NVIDIA no longer common stock
    assert sec.parse(bundle(filing(xml=xml)), SERIES, AT)[0].value == pytest.approx(37.887 - 7.517 + 1.469, abs=0.002)


def test_parse_rejects_a_filing_with_too_few_stock_positions():
    with pytest.raises(SourceError, match="nur 15 Aktienpositionen"):
        sec.parse(bundle(filing()), SERIES, AT)


@pytest.mark.parametrize(
    "item, message",
    [
        (filing(report_date="2026-03-31"), "Stichtag '2026-06-30' statt '2026-03-31'"),
        (filing(xml="<edgarSubmission"), "kein gültiges XML"),
        (filing(xml=XML.replace("<pctVal>7.517011844111</pctVal>", "<pctVal>n/a</pctVal>")), "Anteil unlesbar bei 'NVIDIA Corp'"),
    ],
)
def test_parse_errors_name_the_filing(few_positions, item, message):
    with pytest.raises(SourceError, match=message):
        sec.parse(bundle(item), SERIES, AT)


def test_parse_rejects_an_unreadable_bundle():
    with pytest.raises(SourceError, match="Abrufbündel unlesbar"):
        sec.parse(b'{"filings": [{}]}', SERIES, AT)


def submissions(change=None):
    data = json.loads(SUBMISSIONS)
    if change:
        change(data["filings"]["recent"])
    return json.dumps(data).encode()


def add_amendment(recent):
    for key, value in {"accessionNumber": "0001410368-26-099999", "filingDate": "2026-09-15", "reportDate": "2026-06-30",
                       "acceptanceDateTime": "2026-09-15T16:00:00.000Z", "form": "NPORT-P/A",
                       "primaryDocument": "xslFormNPORT-P_X01/primary_doc.xml"}.items():
        recent[key].insert(0, value)


def test_listing_keeps_the_newest_filing_per_period_and_only_n_port():
    filings = sec._latest_per_period(submissions(add_amendment))
    assert [(f["report_date"], f["accession"], f["form"], f["document"]) for f in filings] == [
        ("2026-03-31", "0001410368-26-055357", "NPORT-P", "primary_doc.xml"),
        ("2026-06-30", "0001410368-26-099999", "NPORT-P/A", "primary_doc.xml"),  # the amendment replaces the original
    ]


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda r: r.update(form=[]), "Spalten unterschiedlich lang"),
        (lambda r: r.pop("reportDate"), "Einreichungsliste unlesbar"),
        (lambda r: r.update(form=["497"] * len(r["form"])), "keine N-PORT-Meldung"),
        (lambda r: r["primaryDocument"].__setitem__(0, "../../x.htm"), "unerwarteter Eintrag"),
        (lambda r: r["reportDate"].__setitem__(0, "30.06.2026"), "Datum unlesbar"),
    ],
)
def test_listing_changes_are_errors(change, message):
    with pytest.raises(SourceError, match=message):
        sec._latest_per_period(submissions(change))


class Client:
    def __init__(self, listing=SUBMISSIONS):
        self.listing, self.calls = listing, []

    def get(self, url, params=None, *, user_agent=None):
        self.calls.append((url, user_agent))
        body = self.listing if url.startswith("https://data.sec.gov/") else XML.encode()
        return Fetched(body, AT, 200)


def test_first_fetch_reads_every_period_later_ones_from_the_newest_stored_period_on():
    client = Client()
    fetched = sec.fetch(client, SERIES)
    urls = [url for url, _ in client.calls]
    assert urls == [
        "https://data.sec.gov/submissions/CIK0000884394.json",
        "https://www.sec.gov/Archives/edgar/data/884394/000141036826055357/primary_doc.xml",
        "https://www.sec.gov/Archives/edgar/data/884394/000141036826089410/primary_doc.xml",
    ]
    assert all(urlsplit(url).hostname in ALLOWED_HOSTS for url in urls)
    assert all(agent == f"{USER_AGENT} {CONTACT}" for _, agent in client.calls)
    assert [f["report_date"] for f in json.loads(fetched.content)["filings"]] == ["2026-03-31", "2026-06-30"]

    client = Client()
    fetched = sec.fetch(client, SERIES, since=date(2026, 6, 30))
    assert len(client.calls) == 2  # the list and the newest period, read again
    assert json.loads(fetched.content)["since"] == "2026-06-30"


@pytest.mark.parametrize("value", ["", "Max Mustermann", "   "])
def test_fetch_needs_a_contact_with_mail_address(monkeypatch, value):
    monkeypatch.setenv("FEVER_SEC_CONTACT", value)
    client = Client()
    with pytest.raises(SourceError, match="FEVER_SEC_CONTACT fehlt"):
        sec.fetch(client, SERIES)
    assert client.calls == []


def only_june(recent):
    keep = [i for i, reported in enumerate(recent["reportDate"]) if reported != "2026-03-31"]
    for key in recent:
        recent[key] = [recent[key][i] for i in keep]


def test_update_stores_the_share_with_an_estimated_release_on_the_first_fetch(migrated_dir, few_positions):
    engine = make_engine(migrated_dir)
    result = update_series(engine, migrated_dir, Client(submissions(only_june)), SERIES, clock=lambda: AT)
    assert result.error is None and result.added == 1
    with engine.connect() as conn:
        row = conn.execute(select(observation).where(observation.c.series_id == "sec_spy_top10")).one()
    assert row.obs_date == date(2026, 6, 30) and row.value == pytest.approx(37.887, abs=0.002)
    # E-14: 30.06.2026 + 62 days = Monday 31.08.2026, 18:00 New York (EDT) = 22:00 UTC; filed on 28.08.2026
    assert row.vintage == datetime(2026, 8, 31, 22, 0, tzinfo=timezone.utc)
    assert row.vintage_estimated
