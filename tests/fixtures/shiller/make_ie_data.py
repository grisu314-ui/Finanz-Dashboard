"""Writes the synthetic test fixture ie_data.xls (decision E-27: format only, no real values).

Layout as in Robert J. Shiller's ie_data.xls of 02.09.2026: sheets "Disclaimer" and "Data",
eight header rows with the original labels, dates as YYYY.MM numbers (October = .1), "NA"
before CAPE starts, a note row below the data. Every number is made up.

Needs xlwt, which is not a project dependency; run it only to rebuild the fixture:
    pip install xlwt==1.3.0 && python tests/fixtures/shiller/make_ie_data.py
"""

from pathlib import Path

import xlwt

HEADER = [
    [""] * 22,
    ['Stock Market Data Used in "Irrational Exuberance" Princeton University Press, 2000, 2005, 2015, updated',
     "", "", "", "", "", "", "", "", "", "", "", "Cyclically", "", "Cyclically ", "", "", "", "", "", "", ""],
    ["Robert J. Shiller ", "", "", "", "", "", "", "", "", "", "", "", "Adjusted", "", "Adjusted", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", "", "", "", "", "Price", "", "Total Return Price", "", "", "", "", "", "", ""],
    ["", "", "", "", "  Consumer", "", "", "", "", "Real", "", "Real", "Earnings", "", "Earnings", "", "", "Monthly",
     "Real", "", "", ""],
    ["", "S&P", "", "", "Price", "", "Long", "", "", "Total", "", "TR", "Ratio", "", "Ratio", "", "Excess", "Total",
     "Total", "10 Year", "10 Year", "Real 10 Year"],
    ["", "Comp.", "Dividend", "Earnings", "Index", "Date  ", "Interest", "Real", "Real", "Return", "Real", "Scaled",
     "P/E10 or", "", "TR P/E10 or", "", "CAPE", "Bond", "Bond", "Annualized Stock", "Annualized Bonds ",
     "Excess Annualized "],
    ["Date", "P", "D", "E", "CPI", "Fraction", "Rate GS10", "Price", "Dividend", "Price", "Earnings", "Earnings",
     "CAPE", "", "TR CAPE", "", "Yield", "Returns", "Returns", "Real Return", "Real Return", "Returns"],
]
# date, CAPE, Excess CAPE Yield ("NA"/None: missing as in the original)
ROWS = [
    (1871.01, "NA", None),
    (1871.02, "NA", None),
    (1881.01, 18.0, -0.01),
    (1881.02, 18.5, -0.005),
    (2025.1, 38.25, 0.0125),
    (2025.11, 38.5, 0.012),
    (2025.12, 39.0, 0.0115),
    (2026.01, 39.5, 0.011),
    (2026.09, 40.0, 0.0105),
]
NOTE = {1: "Sept price is Sept 1st close", 4: "Oct '25/Aug/Sept CPI estimated", 6: "Sept GS10 is Sept 1st value"}


def main() -> None:
    book = xlwt.Workbook()
    book.add_sheet("Disclaimer").write(0, 0, "Synthetic test fixture with made-up values, not Shiller's data.")
    sheet = book.add_sheet("Data")
    for row, labels in enumerate(HEADER):
        for column, label in enumerate(labels):
            if label:
                sheet.write(row, column, label)
    for offset, (stamp, cape, ecy) in enumerate(ROWS):
        row = len(HEADER) + offset
        sheet.write(row, 0, stamp)
        for column in range(1, 22):
            if column not in (12, 13, 14, 15, 16):
                sheet.write(row, column, 100.0 + offset + column / 10)  # made-up filler
        sheet.write(row, 12, cape)
        sheet.write(row, 14, cape if cape == "NA" else cape + 2.0)
        if ecy is not None:
            sheet.write(row, 16, ecy)
    for column, text in NOTE.items():
        sheet.write(len(HEADER) + len(ROWS), column, text)
    book.save(str(Path(__file__).with_name("ie_data.xls")))


if __name__ == "__main__":
    main()
