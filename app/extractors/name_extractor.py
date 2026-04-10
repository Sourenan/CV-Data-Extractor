"""
Name field extractor.
"""

from app.extractors.base import ExtractionStrategy, FieldExtractor


class NameExtractor(FieldExtractor[str | None]):
    """Extracts the candidate name field from resume text.

    Delegates entirely to the injected strategy; holds no extraction
    logic of its own.
    """

    def __init__(self, strategy: ExtractionStrategy[str | None]) -> None:
        self._strategy = strategy

    def extract(self, text: str) -> str | None:
        return self._strategy.extract(text)
