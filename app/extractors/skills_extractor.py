"""
Skills field extractor.
"""

from app.extractors.base import ExtractionStrategy, FieldExtractor


class SkillsExtractor(FieldExtractor[list[str]]):
    """Extracts the skills list from resume text.

    Delegates entirely to the injected strategy; holds no extraction
    logic of its own.
    """

    def __init__(self, strategy: ExtractionStrategy[list[str]]) -> None:
        self._strategy = strategy

    def extract(self, text: str) -> list[str]:
        return self._strategy.extract(text)
