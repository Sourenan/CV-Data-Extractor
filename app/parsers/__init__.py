"""
Parser sub-package.

Exports the FileParser abstract base class and concrete implementations
so callers can import directly from `app.parsers`.
"""

from app.parsers.base import FileParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.word_parser import WordParser

__all__ = ["FileParser", "PDFParser", "WordParser"]
