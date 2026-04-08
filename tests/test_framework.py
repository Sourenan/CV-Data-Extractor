"""
Tests for ResumeParserFramework.
"""

from unittest.mock import MagicMock

import pytest

from app.exceptions import FileParsingError
from app.framework import ResumeParserFramework
from app.models import ResumeData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_framework(
    parser_text: str = "Jane Doe\njane@example.com\nPython",
    resume_data: ResumeData | None = None,
) -> tuple[ResumeParserFramework, MagicMock, MagicMock]:
    """Return a framework wired with mocked parser and extractor."""
    if resume_data is None:
        resume_data = ResumeData(
            name="Jane Doe",
            email="jane@example.com",
            skills=["Python"],
        )

    mock_parser = MagicMock()
    mock_parser.parse.return_value = parser_text

    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = resume_data

    framework = ResumeParserFramework(
        file_parser=mock_parser,
        resume_extractor=mock_extractor,
    )
    return framework, mock_parser, mock_extractor


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestResumeParserFramework:
    def test_returns_resume_data_on_success(self):
        framework, _, _ = _make_framework()
        result = framework.parse_resume("resume.pdf")

        assert isinstance(result, ResumeData)
        assert result.name == "Jane Doe"
        assert result.email == "jane@example.com"
        assert result.skills == ["Python"]

    def test_parser_is_called_with_file_path(self):
        framework, mock_parser, _ = _make_framework()
        framework.parse_resume("/path/to/resume.pdf")
        mock_parser.parse.assert_called_once_with("/path/to/resume.pdf")

    def test_extractor_receives_parser_output(self):
        text = "raw text from parser"
        framework, _, mock_extractor = _make_framework(parser_text=text)
        framework.parse_resume("resume.pdf")
        mock_extractor.extract.assert_called_once_with(text)

    def test_propagates_file_parsing_error_from_parser(self):
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = FileParsingError("bad.pdf", "file not found")

        mock_extractor = MagicMock()

        framework = ResumeParserFramework(
            file_parser=mock_parser,
            resume_extractor=mock_extractor,
        )

        with pytest.raises(FileParsingError):
            framework.parse_resume("bad.pdf")

        # Extractor must not be called when parsing fails
        mock_extractor.extract.assert_not_called()

    def test_empty_text_from_parser_is_passed_to_extractor(self):
        expected = ResumeData(name=None, email=None, skills=[])
        framework, _, mock_extractor = _make_framework(
            parser_text="", resume_data=expected
        )
        result = framework.parse_resume("empty.pdf")
        mock_extractor.extract.assert_called_once_with("")
        assert result.name is None
        assert result.skills == []

    def test_different_file_paths_are_forwarded_correctly(self):
        framework, mock_parser, _ = _make_framework()
        framework.parse_resume("/docs/cv.docx")
        mock_parser.parse.assert_called_once_with("/docs/cv.docx")
