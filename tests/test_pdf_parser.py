"""
Tests for PDFParser.

fitz (PyMuPDF) is mocked throughout so these tests run without a real
PDF file or the PyMuPDF C-extension installed.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import FileParsingError
from app.parsers.pdf_parser import PDFParser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_doc(page_texts: list[str]) -> MagicMock:
    """Return a mock fitz document whose pages yield the given texts."""
    pages = []
    for text in page_texts:
        page = MagicMock()
        page.get_text.return_value = text
        pages.append(page)

    doc = MagicMock()
    doc.__iter__ = lambda self: iter(pages)
    return doc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPDFParser:
    def test_missing_file_raises_file_parsing_error(self):
        parser = PDFParser()
        with pytest.raises(FileParsingError) as exc_info:
            parser.parse("/nonexistent/does_not_exist.pdf")
        assert "file not found" in str(exc_info.value)

    def test_valid_pdf_returns_extracted_text(self, tmp_path):
        fake_pdf = tmp_path / "resume.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        mock_doc = _make_mock_doc(["Jane Doe\n", "jane@example.com\nPython"])
        with patch("app.parsers.pdf_parser.fitz.open", return_value=mock_doc):
            result = PDFParser().parse(str(fake_pdf))

        assert "Jane Doe" in result
        assert "jane@example.com" in result
        assert "Python" in result

    def test_multi_page_pdf_combines_text(self, tmp_path):
        fake_pdf = tmp_path / "multi.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        mock_doc = _make_mock_doc(["Page one text\n", "Page two text\n"])
        with patch("app.parsers.pdf_parser.fitz.open", return_value=mock_doc):
            result = PDFParser().parse(str(fake_pdf))

        assert "Page one text" in result
        assert "Page two text" in result

    def test_fitz_open_failure_raises_file_parsing_error(self, tmp_path):
        fake_pdf = tmp_path / "corrupt.pdf"
        fake_pdf.write_bytes(b"not a real pdf")

        with patch(
            "app.parsers.pdf_parser.fitz.open",
            side_effect=RuntimeError("unsupported format"),
        ):
            with pytest.raises(FileParsingError) as exc_info:
                PDFParser().parse(str(fake_pdf))

        assert "could not open PDF" in str(exc_info.value)

    def test_page_read_failure_raises_file_parsing_error(self, tmp_path):
        fake_pdf = tmp_path / "bad_page.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        bad_page = MagicMock()
        bad_page.get_text.side_effect = RuntimeError("page decode error")
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([bad_page])

        with patch("app.parsers.pdf_parser.fitz.open", return_value=mock_doc):
            with pytest.raises(FileParsingError) as exc_info:
                PDFParser().parse(str(fake_pdf))

        assert "error reading PDF pages" in str(exc_info.value)

    def test_empty_pdf_returns_empty_string(self, tmp_path):
        fake_pdf = tmp_path / "empty.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        mock_doc = _make_mock_doc(["", "   "])
        with patch("app.parsers.pdf_parser.fitz.open", return_value=mock_doc):
            result = PDFParser().parse(str(fake_pdf))

        assert result == ""

    def test_doc_is_closed_even_on_page_error(self, tmp_path):
        """fitz document must be closed even when page iteration fails."""
        fake_pdf = tmp_path / "resume.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        bad_page = MagicMock()
        bad_page.get_text.side_effect = RuntimeError("oops")
        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([bad_page])

        with patch("app.parsers.pdf_parser.fitz.open", return_value=mock_doc):
            with pytest.raises(FileParsingError):
                PDFParser().parse(str(fake_pdf))

        mock_doc.close.assert_called_once()
