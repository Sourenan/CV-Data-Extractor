"""
Extractor sub-package.

Exports the two abstract base classes so callers can import them
directly from `app.extractors`.
"""

from app.extractors.base import ExtractionStrategy, FieldExtractor

__all__ = ["ExtractionStrategy", "FieldExtractor"]
