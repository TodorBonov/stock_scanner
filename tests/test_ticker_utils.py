"""Tests for ticker_utils."""
import pytest
from ticker_utils import clean_ticker, get_possible_ticker_formats, TICKER_MAPPING


def test_clean_ticker_plain():
    assert clean_ticker("AAPL") == "AAPL"
    assert clean_ticker("msft") == "MSFT"


def test_clean_ticker_strips_suffix():
    assert clean_ticker("ASMLa_EQ") == "ASMLA"
    assert clean_ticker("WTAI_EQ") == "WTAI"


def test_clean_ticker_mapping():
    assert clean_ticker("WTAIM_EQ") == "WTAI"
    assert clean_ticker("WTAIm_EQ") == "WTAI"


def test_clean_ticker_empty():
    assert clean_ticker("") == ""


def test_get_possible_ticker_formats():
    formats = get_possible_ticker_formats("AAPL", include_exchange_suffixes=True)
    assert "AAPL" in formats
    assert ".L" in "".join(formats) or any(".L" in f for f in formats)
    assert formats[0] == "AAPL"


def test_get_possible_ticker_formats_no_suffixes():
    formats = get_possible_ticker_formats("WTAI", include_exchange_suffixes=False)
    assert formats == ["WTAI"]
