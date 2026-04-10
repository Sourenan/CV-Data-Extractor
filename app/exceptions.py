"""
Custom exceptions for the CV Data Extractor framework.

Hierarchy
---------
ResumeParserError          -- base for all framework errors
├── UnsupportedFileTypeError  -- file extension not handled
└── FileParsingError          -- low-level I/O or format error while reading a file
"""


class ResumeParserError(Exception):
    """Base exception for all errors raised by this framework."""


class UnsupportedFileTypeError(ResumeParserError):
    """Raised when the file extension has no registered parser."""

    def __init__(self, extension: str) -> None:
        super().__init__(f"No parser available for file type: '{extension}'")
        self.extension = extension


class FileParsingError(ResumeParserError):
    """Raised when a file cannot be read or its content cannot be extracted."""

    def __init__(self, file_path: str, reason: str) -> None:
        super().__init__(f"Failed to parse '{file_path}': {reason}")
        self.file_path = file_path
        self.reason = reason
