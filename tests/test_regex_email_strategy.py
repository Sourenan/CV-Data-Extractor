"""
Tests for RegexEmailStrategy.
"""

import pytest

from app.strategies.regex_email_strategy import RegexEmailStrategy


class TestRegexEmailStrategy:
    def setup_method(self):
        self.strategy = RegexEmailStrategy()

    def test_extracts_plain_email(self):
        text = "Contact me at jane.doe@gmail.com for more info."
        assert self.strategy.extract(text) == "jane.doe@gmail.com"

    def test_returns_lowercase(self):
        text = "Email: Jane.Doe@GMAIL.COM"
        assert self.strategy.extract(text) == "jane.doe@gmail.com"

    def test_strips_surrounding_whitespace(self):
        text = "  jane@example.com  "
        assert self.strategy.extract(text) == "jane@example.com"

    def test_returns_first_email_when_multiple_present(self):
        text = "Primary: a@example.com, Secondary: b@example.com"
        result = self.strategy.extract(text)
        assert result == "a@example.com"

    def test_returns_none_when_no_email(self):
        text = "No contact info here."
        assert self.strategy.extract(text) is None

    def test_returns_none_for_empty_string(self):
        assert self.strategy.extract("") is None

    def test_handles_email_with_plus_tag(self):
        text = "user+tag@domain.co.uk"
        assert self.strategy.extract(text) == "user+tag@domain.co.uk"

    def test_handles_email_with_subdomain(self):
        text = "user@mail.company.org"
        assert self.strategy.extract(text) == "user@mail.company.org"

    def test_handles_email_embedded_in_resume_text(self):
        resume = (
            "Jane Doe\n"
            "Software Engineer\n"
            "jane.doe@company.com | +1-555-0100\n"
            "Skills: Python, Docker\n"
        )
        assert self.strategy.extract(resume) == "jane.doe@company.com"
