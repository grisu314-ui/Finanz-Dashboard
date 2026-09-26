"""Federal Reserve Board: excess bond premium and GZ credit spread (monthly CSV).

source_id is the column name ("ebp", "gz_spread"); both come from one download (group
"fed_ebp", E-36). Updated "sometime after 10:00 a.m. on the fourth business day of each
month" (FEDS Notes, 06.10.2016). Dates are the first day of the month, M/D/YYYY.
"""

from datetime import date, datetime

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, csv_column

URL = "https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv"


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    # `since` is not needed: every request returns the full history.
    return client.get(URL)


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    rows = csv_column(content, "date", "%m/%d/%Y", series.source_id)
    for row in rows:
        if row.obs_date.day != 1:
            raise SourceError(f"{row.obs_date:%d.%m.%Y}: Monatswert nicht auf den Monatsersten datiert")
    return rows
