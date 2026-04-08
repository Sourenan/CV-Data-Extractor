"""
Extractor sub-package.

Exports abstract base classes and all concrete field extractors so
callers can import directly from `app.extractors`.
"""

from app.extractors.base import ExtractionStrategy, FieldExtractor
from app.extractors.email_extractor import EmailExtractor
from app.extractors.name_extractor import NameExtractor
from app.extractors.skills_extractor import SkillsExtractor

__all__ = [
    "ExtractionStrategy",
    "FieldExtractor",
    "EmailExtractor",
    "NameExtractor",
    "SkillsExtractor",
]
