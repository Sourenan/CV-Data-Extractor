"""
Tests for the thin field extractor wrappers.

Each extractor's only job is to delegate to its injected strategy.
These tests verify that delegation contract without caring about
extraction logic (which is tested in the strategy tests).
"""

from unittest.mock import MagicMock

from app.extractors.email_extractor import EmailExtractor
from app.extractors.name_extractor import NameExtractor
from app.extractors.skills_extractor import SkillsExtractor


SAMPLE_TEXT = "Jane Doe\njane@example.com\nPython Docker"


class TestEmailExtractor:
    def test_delegates_to_strategy(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = "jane@example.com"

        extractor = EmailExtractor(strategy=mock_strategy)
        result = extractor.extract(SAMPLE_TEXT)

        mock_strategy.extract.assert_called_once_with(SAMPLE_TEXT)
        assert result == "jane@example.com"

    def test_returns_none_when_strategy_returns_none(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = None

        extractor = EmailExtractor(strategy=mock_strategy)
        assert extractor.extract(SAMPLE_TEXT) is None


class TestNameExtractor:
    def test_delegates_to_strategy(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = "Jane Doe"

        extractor = NameExtractor(strategy=mock_strategy)
        result = extractor.extract(SAMPLE_TEXT)

        mock_strategy.extract.assert_called_once_with(SAMPLE_TEXT)
        assert result == "Jane Doe"

    def test_returns_none_when_strategy_returns_none(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = None

        extractor = NameExtractor(strategy=mock_strategy)
        assert extractor.extract("no name here") is None


class TestSkillsExtractor:
    def test_delegates_to_strategy(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = ["Python", "Docker"]

        extractor = SkillsExtractor(strategy=mock_strategy)
        result = extractor.extract(SAMPLE_TEXT)

        mock_strategy.extract.assert_called_once_with(SAMPLE_TEXT)
        assert result == ["Python", "Docker"]

    def test_returns_empty_list_when_strategy_returns_empty(self):
        mock_strategy = MagicMock()
        mock_strategy.extract.return_value = []

        extractor = SkillsExtractor(strategy=mock_strategy)
        assert extractor.extract("no skills here") == []
