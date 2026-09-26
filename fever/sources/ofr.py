"""OFR Financial Stress Index: one CSV with the index, five categories and three regions.

source_id is the column name, e.g. "OFR FSI" or "Credit"; all columns come from one
download (group "ofr_fsi", E-36). "The FSI publishes with data that is current from
two business days prior" (financialresearch.gov, checked 26.09.2026).
"""

from datetime import date, datetime

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, csv_column

URL = "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv"


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    # `since` is not needed: every request returns the full history.
    return client.get(URL)


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    return csv_column(content, "Date", "%Y-%m-%d", series.source_id)
