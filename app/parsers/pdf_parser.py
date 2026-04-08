"""
PDF parser implementation using PyMuPDF (fitz).

PyMuPDF is chosen over pdfplumber for its speed and reliability on
a wider range of PDF variants. It handles multi-page documents and
returns text page-by-page, which we then join and normalise.
"""

import os

import fitz  # PyMuPDF

from app.exceptions import FileParsingError
from app.parsers.base import FileParser
from app.utils.logger import get_logger
from app.utils.text_utils import normalize_whitespace

logger = get_logger(__name__)


class PDFParser(FileParser):
    """Extracts plain text from a PDF file using PyMuPDF."""

    def parse(self, file_path: str) -> str:
        """Read *file_path* and return its full text content.

        Parameters
        ----------
        file_path:
            Path to a ``.pdf`` file.

        Returns
        -------
        str
            Normalised text extracted from all pages. Empty string if
            the PDF contains no selectable text (e.g. scanned image only).

        Raises
        ------
        FileParsingError
            If the file does not exist, cannot be opened, or PyMuPDF
            raises an unrecoverable error.
        """
        if not os.path.isfile(file_path):
            raise FileParsingError(file_path, "file not found")

        logger.info("Parsing PDF: %s", file_path)

        try:
            doc = fitz.open(file_path)
        except Exception as exc:
            raise FileParsingError(file_path, f"could not open PDF: {exc}") from exc

        try:
            pages: list[str] = []
            for page in doc:
                pages.append(page.get_text())
        except Exception as exc:
            raise FileParsingError(
                file_path, f"error reading PDF pages: {exc}"
            ) from exc
        finally:
            doc.close()

        raw_text = "\n".join(pages)
        text = normalize_whitespace(raw_text)

        if not text:
            logger.warning("PDF produced no extractable text: %s", file_path)

        logger.debug("Extracted %d characters from PDF: %s", len(text), file_path)
        return text
