import pytest

from fever.config import CONFIG_DIR, ConfigError, indicator_catalog, load, scoring_config


def write(tmp_path, name, text):
    (tmp_path / f"{name}.toml").write_text(text, encoding="utf-8")
    return tmp_path


def test_repository_config_files_load():
    assert isinstance(load("series"), dict)
    assert isinstance(load("scoring"), dict)


def test_series_tables_load(tmp_path):
    config_dir = write(tmp_path, "series", '[series.vix]\nsource = "cboe"\n\n[indicator.vix_level]\n')
    data = load("series", config_dir)
    assert data["series"]["vix"]["source"] == "cboe"
    assert data["indicator"]["vix_level"] == {}


def test_unknown_file_name_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match="Unbekannte Konfigurationsdatei"):
        load("secrets", tmp_path)


def test_missing_file_names_the_path(tmp_path):
    with pytest.raises(ConfigError, match="series.toml"):
        load("series", tmp_path)


def test_invalid_toml_names_the_path(tmp_path):
    config_dir = write(tmp_path, "series", "[series.vix\n")
    with pytest.raises(ConfigError, match="Ungültiges TOML .*series.toml"):
        load("series", config_dir)


def test_unknown_top_level_entry_is_rejected(tmp_path):
    config_dir = write(tmp_path, "series", "[serie.vix]\n")
    with pytest.raises(ConfigError, match="Unbekannte Einträge .*serie"):
        load("series", config_dir)


def test_top_level_entry_must_be_a_table(tmp_path):
    config_dir = write(tmp_path, "series", "series = 1\n")
    with pytest.raises(ConfigError, match="'series' .* muss eine Tabelle sein"):
        load("series", config_dir)


def test_series_entry_must_be_a_table(tmp_path):
    config_dir = write(tmp_path, "series", "[series]\nvix = 1\n")
    with pytest.raises(ConfigError, match="'series.vix' .* muss eine Tabelle sein"):
        load("series", config_dir)


def test_scoring_rejects_unknown_tables(tmp_path):
    config_dir = write(tmp_path, "scoring", "[matrix]\nred = 90\n")
    with pytest.raises(ConfigError, match="Unbekannte Einträge"):
        load("scoring", config_dir)


# --- scoring.toml and [indicator.*] (M5) ------------------------------------------------------------

SCORING = (CONFIG_DIR / "scoring.toml").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "old, new, message",
    [
        ("hysteresis = 5 ", "", "scoring.rules: Parameter fehlen: hysteresis"),
        ("hysteresis = 5 ", "hysteresis = 5\nhysterese = 5\n", "unbekannte Parameter: hysterese"),
        ("min_blocks = 3 ", "min_blocks = 3.5 ", "min_blocks muss eine ganze Zahl > 0 sein"),
        ("red_stress = 90", "red_stress = 190", "red_stress: höchstens 100"),
        ("red_stress = 90", 'red_stress = "90"', "red_stress muss eine Zahl > 0 sein"),
        ('fast_block = "volatility"', 'fast_block = "vola"', "unbekannter Block 'vola'"),
        ("min_history_years = 5 ", "min_history_years = 11 ", "display_window_years < min_history_years <= window_years"),
    ],
)
def test_scoring_parameters_are_checked(tmp_path, old, new, message):
    assert SCORING.count(old) == 1
    with pytest.raises(ConfigError, match=message):
        scoring_config(write(tmp_path, "scoring", SCORING.replace(old, new)))


def test_repository_scoring_parameters():
    config = scoring_config()
    assert (config.window_years, config.min_history_years, config.min_blocks, config.hysteresis) == (10, 5, 3, 5.0)


SERIES = (CONFIG_DIR / "series.toml").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "old, new, message",
    [
        ('series = ["vix", "vix3m"]', 'series = ["vix"]', "indicator.vix_vix3m: 'ratio' braucht 2 Reihe"),
        ('series = ["vix", "vix3m"]', 'series = ["vix", "vix4m"]', "unbekannte Reihe\\(n\\): vix4m"),
        ('series = ["vix", "vix3m"]', 'series = ["vix", "nfci"]', "dieselbe Frequenz"),
        ('transform = "above_low"', 'transform = "above_min"', "unbekannte Transformation"),
        ('orientation = "low"\nblock = "volatility"', 'orientation = "down"\nblock = "volatility"', "'orientation' muss"),
        ('block = "credit"\nv_score = 4', 'block = "kredit"\nv_score = 4', "unbekannter Block 'kredit'"),
        ('block = "credit"\nv_score = 4', 'block = "credit"\nv_score = 6', "'v_score' muss eine ganze Zahl von 1 bis 5"),
        ("display_window = true", 'display_window = "ja"', "'display_window' muss true oder false"),
        ('v_score = 4\n', 'v_score = 4\nweight = 2\n', "unbekannte Felder: weight"),
    ],
)
def test_indicators_are_checked(tmp_path, old, new, message):
    assert SERIES.count(old) == 1, old
    with pytest.raises(ConfigError, match=message):
        indicator_catalog(write(tmp_path, "series", SERIES.replace(old, new)))
