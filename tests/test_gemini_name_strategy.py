"""
Tests for GeminiNameStrategy.

No real API key or SDK is needed.  We pass lightweight fake clients that
satisfy the LLMClient Protocol.
"""

import pytest

from app.strategies.gemini_name_strategy import GeminiNameStrategy, LLMClient


# ---------------------------------------------------------------------------
# Fake clients
# ---------------------------------------------------------------------------

class _FakeResponse:
    """Minimal response object with a .text attribute."""
    def __init__(self, text: str) -> None:
        self.text = text


class _SuccessClient:
    """Client that always returns a fixed name."""
    def __init__(self, name: str) -> None:
        self._name = name

    def generate_content(self, prompt: str) -> _FakeResponse:
        return _FakeResponse(self._name)


class _EmptyClient:
    """Client that returns an empty string."""
    def generate_content(self, prompt: str) -> _FakeResponse:
        return _FakeResponse("")


class _RaisingClient:
    """Client that always raises an exception."""
    def generate_content(self, prompt: str) -> _FakeResponse:
        raise RuntimeError("API timeout")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGeminiNameStrategy:
    def test_returns_name_from_client_response(self):
        strategy = GeminiNameStrategy(client=_SuccessClient("Jane Doe"))
        result = strategy.extract("Jane Doe\njane@example.com\nPython")
        assert result == "Jane Doe"

    def test_strips_whitespace_from_response(self):
        strategy = GeminiNameStrategy(client=_SuccessClient("  Jane Doe  "))
        result = strategy.extract("some resume text")
        assert result == "Jane Doe"

    def test_strips_quotes_from_response(self):
        strategy = GeminiNameStrategy(client=_SuccessClient('"Jane Doe"'))
        result = strategy.extract("some resume text")
        assert result == "Jane Doe"

    def test_strips_name_label_prefix(self):
        # LLM sometimes returns "Name: Jane Doe" despite prompt instructions
        strategy = GeminiNameStrategy(client=_SuccessClient("Name: Jane Doe"))
        result = strategy.extract("some resume text")
        assert result == "Jane Doe"

    def test_strips_full_name_label_prefix(self):
        strategy = GeminiNameStrategy(client=_SuccessClient("Full Name: John Smith"))
        result = strategy.extract("some resume text")
        assert result == "John Smith"

    def test_returns_none_when_client_returns_empty_string(self):
        strategy = GeminiNameStrategy(client=_EmptyClient())
        result = strategy.extract("some resume text")
        assert result is None

    def test_returns_none_when_client_raises(self):
        strategy = GeminiNameStrategy(client=_RaisingClient())
        result = strategy.extract("some resume text")
        assert result is None

    def test_returns_none_for_empty_input_text(self):
        strategy = GeminiNameStrategy(client=_SuccessClient("Jane Doe"))
        # Should short-circuit before calling the client
        result = strategy.extract("")
        assert result is None

    def test_client_not_called_for_empty_text(self):
        """Client should not be invoked at all when text is empty."""
        call_count = []

        class _TrackingClient:
            def generate_content(self, prompt: str) -> _FakeResponse:
                call_count.append(1)
                return _FakeResponse("Jane Doe")

        strategy = GeminiNameStrategy(client=_TrackingClient())
        strategy.extract("")
        assert len(call_count) == 0

    def test_fake_client_satisfies_llm_client_protocol(self):
        """Verify our fake clients are recognised as LLMClient at runtime."""
        assert isinstance(_SuccessClient("x"), LLMClient)
        assert isinstance(_EmptyClient(), LLMClient)
        assert isinstance(_RaisingClient(), LLMClient)
