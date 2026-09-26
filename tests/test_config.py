import pytest

from fever.config import ConfigError, load


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


def test_scoring_accepts_no_parameters_before_m5(tmp_path):
    config_dir = write(tmp_path, "scoring", "[matrix]\nred = 90\n")
    with pytest.raises(ConfigError, match="Unbekannte Einträge"):
        load("scoring", config_dir)
