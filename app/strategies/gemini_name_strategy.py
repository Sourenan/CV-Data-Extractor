"""
LLM-based name extraction strategy using Google Gemini.

Design for testability
----------------------
``GeminiNameStrategy`` depends on an ``LLMClient`` Protocol, not on the
Gemini SDK class directly.  In production, pass a real
``google.generativeai.GenerativeModel`` instance.  In tests, pass any
object that satisfies the protocol — no monkeypatching required.

The real Gemini SDK is only imported lazily (inside ``from_api_key``)
so the rest of the codebase can be imported and tested without the SDK
installed, as long as you never call ``from_api_key`` in those tests.
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from app.extractors.base import ExtractionStrategy
from app.utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_TEMPLATE = (
    "You are a resume parser. "
    "Read the resume text below and return ONLY the candidate's full name "
    "as a plain string — no punctuation, no labels, no explanation.\n\n"
    "Resume:\n{text}\n\n"
    "Full name:"
)


@runtime_checkable
class LLMClient(Protocol):
    """Minimal interface required by GeminiNameStrategy.

    Any object with a ``generate_content(prompt: str)`` method whose
    return value has a ``.text`` attribute satisfies this protocol.
    This makes the strategy trivially mockable without a real API key.
    """

    def generate_content(self, prompt: str) -> object:
        """Send *prompt* to the model and return a response object."""
        ...  # pragma: no cover


class GeminiNameStrategy(ExtractionStrategy[str | None]):
    """Extracts the candidate's full name via a Gemini LLM call.

    Parameters
    ----------
    client:
        Any object satisfying the ``LLMClient`` protocol.  In production
        this is a ``google.generativeai.GenerativeModel`` instance.
    """

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Factory helper — keeps SDK import isolated from the rest of the code
    # ------------------------------------------------------------------

    @classmethod
    def from_api_key(cls, api_key: str, model: str = "gemini-1.5-flash") -> "GeminiNameStrategy":
        """Convenience constructor that creates a real Gemini client.

        Parameters
        ----------
        api_key:
            Your Google AI API key.  Read this from an environment
            variable; never hard-code it.
        model:
            Gemini model identifier.
        """
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=api_key)
        client = genai.GenerativeModel(model)
        return cls(client)

    # ------------------------------------------------------------------
    # Strategy implementation
    # ------------------------------------------------------------------

    def extract(self, text: str) -> str | None:
        if not text:
            return None

        prompt = _PROMPT_TEMPLATE.format(text=text[:3000])  # guard against huge docs

        try:
            response = self._client.generate_content(prompt)
            raw: str = response.text  # type: ignore[attr-defined]
        except Exception as exc:
            logger.warning("Gemini name extraction failed: %s", exc)
            return None

        return _clean_name(raw)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clean_name(raw: str) -> str | None:
    """Strip whitespace, quotes, and common LLM artifacts from name output."""
    name = raw.strip().strip('"').strip("'")
    # Remove leading labels the model might still emit, e.g. "Name: Jane Doe"
    name = re.sub(r"(?i)^(full\s+)?name\s*:\s*", "", name).strip()
    return name if name else None
