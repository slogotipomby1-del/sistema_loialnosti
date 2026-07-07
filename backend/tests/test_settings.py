from pathlib import Path

from config import settings


def test_parse_database_url_for_postgres():
    config = settings.parse_database_url("postgres://demo:secret@db.example.com:5432/referral_db")

    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["NAME"] == "referral_db"
    assert config["USER"] == "demo"
    assert config["PASSWORD"] == "secret"
    assert config["HOST"] == "db.example.com"
    assert config["PORT"] == 5432


def test_parse_database_url_returns_sqlite_for_empty_value(tmp_path: Path):
    config = settings.parse_database_url("", base_dir=tmp_path)

    assert config["ENGINE"] == "django.db.backends.sqlite3"
    assert config["NAME"] == tmp_path / "db.sqlite3"


def test_parse_env_list_splits_and_trims_values():
    values = settings.parse_env_list(" example.com, admin.example.com ,, localhost ")

    assert values == ["example.com", "admin.example.com", "localhost"]
