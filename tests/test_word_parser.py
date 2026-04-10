"""
Tests for WordParser.

python-docx's Document class is mocked so these tests run without a
real .docx file.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import FileParsingError
from app.parsers.word_parser import WordParser

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_doc(
    paragraph_texts: list[str],
    table_cell_texts: list[list[str]] | None = None,
) -> MagicMock:
    """Return a mock python-docx Document.

    Parameters
    ----------
    paragraph_texts:
        Text for each paragraph in order.
    table_cell_texts:
        Optional list of rows, each row being a list of cell text values.
        All rows belong to a single table.
    """
    paragraphs = []
    for text in paragraph_texts:
        p = MagicMock()
        p.text = text
        paragraphs.append(p)

    tables = []
    if table_cell_texts:
        rows = []
        for row_texts in table_cell_texts:
            cells = []
            for cell_text in row_texts:
                cell = MagicMock()
                cell.text = cell_text
                cells.append(cell)
            row = MagicMock()
            row.cells = cells
            rows.append(row)
        table = MagicMock()
        table.rows = rows
        tables.append(table)

    doc = MagicMock()
    doc.paragraphs = paragraphs
    doc.tables = tables
    return doc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestWordParser:
    def test_missing_file_raises_file_parsing_error(self):
        parser = WordParser()
        with pytest.raises(FileParsingError) as exc_info:
            parser.parse("/nonexistent/does_not_exist.docx")
        assert "file not found" in str(exc_info.value)

    def test_valid_docx_returns_extracted_text(self, tmp_path):
        fake_docx = tmp_path / "resume.docx"
        fake_docx.write_bytes(b"placeholder")

        mock_doc = _make_mock_doc(["Jane Doe", "jane@example.com", "Python"])
        with patch("app.parsers.word_parser.Document", return_value=mock_doc):
            result = WordParser().parse(str(fake_docx))

        assert "Jane Doe" in result
        assert "jane@example.com" in result
        assert "Python" in result

    def test_table_cell_text_is_included(self, tmp_path):
        fake_docx = tmp_path / "resume.docx"
        fake_docx.write_bytes(b"placeholder")

        mock_doc = _make_mock_doc(
            paragraph_texts=["Work Experience"],
            table_cell_texts=[["Python", "Docker"]],
        )
        with patch("app.parsers.word_parser.Document", return_value=mock_doc):
            result = WordParser().parse(str(fake_docx))

        assert "Python" in result
        assert "Docker" in result
        assert "Work Experience" in result

    def test_document_open_failure_raises_file_parsing_error(self, tmp_path):
        fake_docx = tmp_path / "corrupt.docx"
        fake_docx.write_bytes(b"not a docx")

        with patch(
            "app.parsers.word_parser.Document",
            side_effect=Exception("bad zip file"),
        ):
            with pytest.raises(FileParsingError) as exc_info:
                WordParser().parse(str(fake_docx))

        assert "could not open Word document" in str(exc_info.value)

    def test_empty_document_returns_empty_string(self, tmp_path):
        fake_docx = tmp_path / "empty.docx"
        fake_docx.write_bytes(b"placeholder")

        mock_doc = _make_mock_doc(paragraph_texts=[], table_cell_texts=None)
        with patch("app.parsers.word_parser.Document", return_value=mock_doc):
            result = WordParser().parse(str(fake_docx))

        assert result == ""

    def test_whitespace_only_paragraphs_produce_empty_string(self, tmp_path):
        fake_docx = tmp_path / "whitespace.docx"
        fake_docx.write_bytes(b"placeholder")

        mock_doc = _make_mock_doc(paragraph_texts=["   ", "\t", ""])
        with patch("app.parsers.word_parser.Document", return_value=mock_doc):
            result = WordParser().parse(str(fake_docx))

        assert result == ""
