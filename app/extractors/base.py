"""
Abstract base classes for field extraction.

Design
------
Two concerns are separated deliberately:

* ``ExtractionStrategy[T]`` — *how* to extract a value (regex, NER, LLM, …).
  Strategies are self-contained and easily swapped or tested in isolation.

* ``FieldExtractor[T]`` — *what* field to extract. Each concrete extractor
  (NameExtractor, EmailExtractor, SkillsExtractor) owns exactly one strategy
  and delegates to it. This keeps extractors thin and makes the strategy
  the single point of variation per field.

Both are generic so that SkillsExtractor can type-check as
``FieldExtractor[list[str]]`` while NameExtractor types as
``FieldExtractor[str | None]``.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class ExtractionStrategy(ABC, Generic[T]):
    """Encapsulates one technique for extracting a value from raw text."""

    @abstractmethod
    def extract(self, text: str) -> T:
        """Apply the strategy to *text* and return the extracted value.

        Parameters
        ----------
        text:
            Plain-text content of the resume.

        Returns
        -------
        T
            The extracted value, or an appropriate empty/null sentinel
            (``None``, ``[]``) when nothing is found.
        """


class FieldExtractor(ABC, Generic[T]):
    """Thin wrapper that binds a field name to its extraction strategy.

    Concrete subclasses accept an ``ExtractionStrategy`` at construction
    time, making the strategy swappable without subclassing the extractor.
    """

    @abstractmethod
    def extract(self, text: str) -> T:
        """Delegate to the underlying strategy and return the field value.

        Parameters
        ----------
        text:
            Plain-text content of the resume.

        Returns
        -------
        T
            The extracted value for this field.
        """
