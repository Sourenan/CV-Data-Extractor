"""
Regex-based email extraction strategy.
"""

import re

from app.extractors.base import ExtractionStrategy

# RFC-5321-compliant enough for resume parsing; readable over perfect.
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


class RegexEmailStrategy(ExtractionStrategy[str | None]):
    """Extracts the first email address found in resume text using regex.

    Returns a lowercased, stripped email string, or ``None`` if no
    email address is present.
    """

    def extract(self, text: str) -> str | None:
        if not text:
            return None

        match = _EMAIL_RE.search(text)
        if match is None:
            return None

        return match.group(0).strip().lower()
