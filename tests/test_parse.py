"""Tests for the data-import parse helpers."""
import pytest
from backend.scripts.import_data import parse_meta, parse_rt, parse_int, parse_float


class TestParseMeta:
    def test_hours_and_minutes(self):
        assert parse_meta("2004, 1 ч 44 мин") == {"year": 2004, "duration_min": 104}

    def test_hours_only(self):
        assert parse_meta("1972, 2 ч") == {"year": 1972, "duration_min": 120}

    def test_minutes_only(self):
        assert parse_meta("2025, 51 мин") == {"year": 2025, "duration_min": 51}

    def test_multi_hour(self):
        assert parse_meta("2001, 2 ч 58 мин") == {"year": 2001, "duration_min": 178}

    def test_none_input(self):
        assert parse_meta(None) == {"year": None, "duration_min": None}

    def test_empty_string(self):
        assert parse_meta("") == {"year": None, "duration_min": None}

    def test_garbage_input(self):
        assert parse_meta("not a date") == {"year": None, "duration_min": None}


class TestParseRT:
    def test_extracts_rt_score(self):
        ratings = [
            {"Source": "Internet Movie Database", "Value": "9.2/10"},
            {"Source": "Rotten Tomatoes", "Value": "97%"},
        ]
        assert parse_rt(ratings) == 97

    def test_returns_none_when_rt_absent(self):
        ratings = [{"Source": "Internet Movie Database", "Value": "9.2/10"}]
        assert parse_rt(ratings) is None

    def test_empty_list(self):
        assert parse_rt([]) is None

    def test_none_input(self):
        assert parse_rt(None) is None

    def test_malformed_value(self):
        ratings = [{"Source": "Rotten Tomatoes", "Value": "N/A"}]
        assert parse_rt(ratings) is None

    def test_zero_percent(self):
        ratings = [{"Source": "Rotten Tomatoes", "Value": "0%"}]
        assert parse_rt(ratings) == 0

    def test_hundred_percent(self):
        ratings = [{"Source": "Rotten Tomatoes", "Value": "100%"}]
        assert parse_rt(ratings) == 100


class TestParseInt:
    def test_plain_number(self):
        assert parse_int("42") == 42

    def test_comma_formatted(self):
        assert parse_int("91,644") == 91644

    def test_millions(self):
        assert parse_int("2,800,000") == 2800000

    def test_na_returns_none(self):
        assert parse_int("N/A") is None

    def test_empty_returns_none(self):
        assert parse_int("") is None

    def test_none_returns_none(self):
        assert parse_int(None) is None


class TestParseFloat:
    def test_valid_float(self):
        assert parse_float("9.3") == 9.3

    def test_integer_string(self):
        assert parse_float("7") == 7.0

    def test_na_returns_none(self):
        assert parse_float("N/A") is None

    def test_empty_returns_none(self):
        assert parse_float("") is None

    def test_none_returns_none(self):
        assert parse_float(None) is None
