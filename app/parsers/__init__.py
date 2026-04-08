"""
Parser sub-package.

Exports the FileParser abstract base class so callers can import
directly from `app.parsers` without knowing the internal module layout.
"""

from app.parsers.base import FileParser

__all__ = ["FileParser"]
