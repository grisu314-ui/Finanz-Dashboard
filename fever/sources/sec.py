"""SEC EDGAR: concentration of the SPDR S&P 500 ETF Trust from its N-PORT filings (E-71, E-74).

The fund reports its full portfolio each quarter-end in Form N-PORT; the public filings start with
the report date 30.09.2019 and come 49 to 62 days after it (28 filings, checked 28.09.2026). Value:
the share of the ten largest issuers in net assets, in percent. Common stock only; share classes
of one company count together, recognised by the issuer's LEI (the name where the LEI is "N/A").

source_id: the fund's CIK. fetch() reads the list of filings and the XML of every filing whose
report date is not older than `since` (the newest stored report date), so the newest period is
read again on each fetch and an amendment (NPORT-P/A) replaces its original. Per report date the
newest filing counts. The bundle goes to the raw archive as JSON. Filings beyond the "recent"
list of the submissions file are not read; for this fund that list holds all of them.

The SEC asks every automated client for a User-Agent with a contact; it comes from
FEVER_SEC_CONTACT in the stack's .env (not secret, but personal, so never in the repository).
Information on sec.gov "may be copied or further distributed ... without the SEC's permission".
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime

from fever.config import Series
from fever.http import USER_AGENT, Fetched, HttpClient
from fever.sources import Row, SourceError, checked

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
DOCUMENT_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}"
FORMS = ("NPORT-P", "NPORT-P/A")
TOP = 10
MIN_POSITIONS = 100  # fewer common stock positions means a changed format, not an S&P 500 fund
NS = {"n": "http://www.sec.gov/edgar/nport"}
_CIK = re.compile(r"\d{10}")
_ACCESSION = re.compile(r"\d{10}-\d{2}-\d{6}")
_DOCUMENT = re.compile(r"[\w.-]+\.xml")
_LEI = re.compile(r"[A-Z0-9]{20}")
_CONTACT = re.compile(r"\S+@\S+\.\S+")


def contact_agent() -> str:
    """User-Agent with the contact from FEVER_SEC_CONTACT; a SourceError if it is missing."""
    contact = " ".join(os.environ.get("FEVER_SEC_CONTACT", "").split())
    if not _CONTACT.search(contact):
        raise SourceError("FEVER_SEC_CONTACT fehlt oder enthält keine E-Mail-Adresse (.env, docs/einrichtung.md)")
    return f"{USER_AGENT} {contact}"


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    agent = contact_agent()
    if not _CIK.fullmatch(series.source_id):
        raise SourceError(f"ungültige CIK {series.source_id!r} (erwartet zehn Ziffern)")
    listing = client.get(SUBMISSIONS_URL.format(cik=series.source_id), user_agent=agent)
    filings = _latest_per_period(listing.content)
    chosen = [f for f in filings if since is None or f["report_date"] >= since.isoformat()]
    last, documents = listing, []
    for filing in chosen:
        url = DOCUMENT_URL.format(cik=int(series.source_id), accession=filing["accession"].replace("-", ""),
                                  document=filing["document"])
        last = client.get(url, user_agent=agent)
        try:
            documents.append({**filing, "xml": last.content.decode("utf-8")})
        except UnicodeDecodeError:
            raise SourceError(f"{filing['accession']}: kein lesbares XML") from None
    bundle = {"since": None if since is None else since.isoformat(), "filings": documents}
    return Fetched(json.dumps(bundle, sort_keys=True).encode(), last.retrieved_at, 200)


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    try:
        filings = json.loads(content)["filings"]
        rows = [_row(filing["accession"], filing["report_date"], filing["xml"]) for filing in filings]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Abrufbündel unlesbar") from None
    return checked(rows)


def top_share(positions: list[tuple[str, str, float]], top: int = TOP) -> float:
    """Sum of the `top` largest issuer shares; positions are (LEI, name, percent of net assets)."""
    issuers: dict[str, float] = {}
    for lei, name, share in positions:
        key = lei if _LEI.fullmatch(lei) else f"name:{name.strip().upper()}"
        issuers[key] = issuers.get(key, 0.0) + share
    return sum(sorted(issuers.values(), reverse=True)[:top])


def _latest_per_period(content: bytes) -> list[dict]:
    """N-PORT filings from the submissions file, the newest per report date, oldest period first."""
    try:
        recent = json.loads(content)["filings"]["recent"]
        columns = [recent[key] for key in ("form", "accessionNumber", "filingDate", "reportDate", "primaryDocument")]
    except (ValueError, KeyError, TypeError):
        raise SourceError("Einreichungsliste unlesbar (filings.recent)") from None
    if len({len(column) for column in columns}) != 1:
        raise SourceError("Einreichungsliste: Spalten unterschiedlich lang")
    newest: dict[str, dict] = {}
    for form, accession, filed, reported, document in zip(*columns):
        if form not in FORMS:
            continue
        # The list names the rendered view ("xslFormNPORT-P_X01/primary_doc.xml"); the XML itself
        # lies under the bare file name in the filing's folder (checked 28.09.2026).
        document = str(document).rsplit("/", 1)[-1]
        if not (_ACCESSION.fullmatch(str(accession)) and _DOCUMENT.fullmatch(document)):
            raise SourceError(f"Einreichungsliste: unerwarteter Eintrag {accession!r} / {document!r}")
        try:
            date.fromisoformat(filed), date.fromisoformat(reported)
        except (TypeError, ValueError):
            raise SourceError(f"{accession}: Datum unlesbar ({filed!r}, {reported!r})") from None
        filing = {"accession": accession, "filing_date": filed, "report_date": reported, "document": document, "form": form}
        known = newest.get(reported)
        if known is None or (filed, accession) > (known["filing_date"], known["accession"]):
            newest[reported] = filing
    if not newest:
        raise SourceError("keine N-PORT-Meldung in der Einreichungsliste")
    return [newest[reported] for reported in sorted(newest)]


def _row(accession: str, report_date: str, xml: str) -> Row:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise SourceError(f"{accession}: kein gültiges XML ({exc})") from None
    reported = root.findtext("n:formData/n:genInfo/n:repPdDate", namespaces=NS)
    if reported != report_date:
        raise SourceError(f"{accession}: Stichtag {reported!r} statt {report_date!r} wie in der Einreichungsliste")
    positions = []
    for item in root.iterfind("n:formData/n:invstOrSecs/n:invstOrSec", NS):
        if item.findtext("n:assetCat", namespaces=NS) != "EC" or item.findtext("n:payoffProfile", namespaces=NS) != "Long":
            continue
        try:
            share = float(item.findtext("n:pctVal", namespaces=NS))
        except (TypeError, ValueError):
            raise SourceError(f"{accession}: Anteil unlesbar bei {item.findtext('n:name', '', NS)[:40]!r}") from None
        positions.append((item.findtext("n:lei", "", NS).strip(), item.findtext("n:name", "", NS), share))
    if len(positions) < MIN_POSITIONS:
        raise SourceError(f"{accession}: nur {len(positions)} Aktienpositionen (erwartet mindestens {MIN_POSITIONS})")
    return Row(date.fromisoformat(report_date), top_share(positions))
