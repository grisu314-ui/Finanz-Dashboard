from datetime import date, time

import pytest

from fever.config import STANDARD_TOLERANCE_DAYS, ConfigError, series_catalog

# Decision E-20: the 23 raw series of M2 part B.
EXPECTED_IDS = {
    "vix", "vix9d", "vix3m", "vix6m", "vvix", "skew",
    "bamlh0a0hym2", "bamlh0a1hybb", "bamlh0a3hyc", "bamlc0a0cm", "bamlc0a4cbbb",
    "nfci", "anfci", "stlfsi4", "t10y3m", "t10y2y", "sahmrealtime",
    "icsa", "ic4wsa", "sofr", "iorb", "sp500", "dgs10",
}

VALID = """
[series.vix]
source = "cboe"
source_id = "VIX"
name = "Cboe Volatility Index (VIX)"
unit = "Indexpunkte"
frequency = "daily"
release_time = "22:00"
lag_days = 0
tolerance_days = 3
bounds = [1, 300]
"""


def catalog_from(tmp_path, text):
    (tmp_path / "series.toml").write_text(text, encoding="utf-8")
    return series_catalog(tmp_path)


def test_repository_catalog_is_valid_and_complete():
    catalog = series_catalog()
    assert set(catalog) == EXPECTED_IDS
    for series in catalog.values():
        assert series.id == series.source_id.lower()


def test_repository_tolerances_follow_e10_or_give_a_reason():
    for series in series_catalog().values():
        standard = STANDARD_TOLERANCE_DAYS[series.frequency]
        assert series.tolerance_days == standard or series.tolerance_reason, series.id


def test_repository_special_cases_are_configured():
    catalog = series_catalog()
    assert catalog["vvix"].start == date(2007, 1, 3)  # E-24
    assert catalog["iorb"].lead_days == 7  # E-25
    assert all(s.lead_days == 0 for s in catalog.values() if s.id != "iorb")
    for series_id in ("bamlh0a0hym2", "bamlh0a1hybb", "bamlh0a3hyc", "bamlc0a0cm", "bamlc0a4cbbb", "sp500"):
        assert "keine Weitergabe" in catalog[series_id].license


def test_valid_entry_fields(tmp_path):
    series = catalog_from(tmp_path, VALID)["vix"]
    assert series.release_time == time(22, 0)
    assert (series.lower, series.upper) == (1.0, 300.0)
    assert series.start is None and series.lead_days == 0


@pytest.mark.parametrize(
    "change, message",
    [
        (('source = "cboe"', 'source = "yahoo"'), "unbekannte Quelle"),
        (('source_id = "VIX"', 'source_id = "VXX"'), "Quellkennung"),
        (('frequency = "daily"', 'frequency = "hourly"'), "unbekannte Frequenz"),
        (('release_time = "22:00"', 'release_time = "22:00:00"'), "release_time"),
        (('release_time = "22:00"', 'release_time = "24:00"'), "release_time"),
        (("lag_days = 0", "lag_days = -1"), "lag_days"),
        (("lag_days = 0", "lag_days = 1.5"), "lag_days"),
        (("tolerance_days = 3", "tolerance_days = 5"), "tolerance_reason"),
        (("bounds = [1, 300]", "bounds = [300, 1]"), "bounds"),
        (("bounds = [1, 300]", "bounds = [1]"), "bounds"),
        (("bounds = [1, 300]", 'bounds = [1, "300"]'), "bounds"),
        (('name = "Cboe Volatility Index (VIX)"', 'name = " "'), "name"),
        (('unit = "Indexpunkte"', 'unit = "Indexpunkte"\ncolour = "red"'), "unbekannte Felder"),
        (('unit = "Indexpunkte"', 'unit = "Indexpunkte"\nstart = 2007-01-03T00:00:00'), "start"),
        (('unit = "Indexpunkte"', 'unit = "Indexpunkte"\nlead_days = -2'), "lead_days"),
        (('unit = "Indexpunkte"', 'unit = "Indexpunkte"\ntolerance_reason = "weil"'), "ohne Abweichung"),
        (("tolerance_days = 3\n", ""), "Pflichtfelder fehlen: tolerance_days"),
    ],
)
def test_invalid_entries_name_the_series_and_the_problem(tmp_path, change, message):
    old, new = change
    assert VALID.count(old) == 1
    with pytest.raises(ConfigError, match=f"series.vix: .*{message}"):
        catalog_from(tmp_path, VALID.replace(old, new))


def test_tolerance_deviation_with_reason_is_accepted(tmp_path):
    text = VALID.replace("tolerance_days = 3", 'tolerance_days = 5\ntolerance_reason = "Quelle veröffentlicht unregelmäßig"')
    assert catalog_from(tmp_path, text)["vix"].tolerance_days == 5


def test_table_key_must_be_a_valid_lower_case_id(tmp_path):
    with pytest.raises(ConfigError, match="series.VIX: .*Kleinbuchstaben"):
        catalog_from(tmp_path, VALID.replace("[series.vix]", "[series.VIX]"))


def test_same_source_id_twice_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match="Ungültiges TOML"):
        catalog_from(tmp_path, VALID + VALID)
