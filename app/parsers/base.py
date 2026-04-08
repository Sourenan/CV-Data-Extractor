"""
Abstract base class for file parsers.

A FileParser is responsible for a single concern: reading a file from
disk and returning its plain-text content. It knows nothing about which
fields to extract — that is the responsibility of the extractor layer.
"""

from abc import ABC, abstractmethod


class FileParser(ABC):
    """Converts a supported file into a plain-text string."""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Read *file_path* and return its full text content.

        Parameters
        ----------
        file_path:
            Absolute or relative path to the resume file.

        Returns
        -------
        str
            The raw text extracted from the file. May be empty if the
            document contains no readable text.

        Raises
        ------
        FileParsingError
            If the file cannot be opened or its content cannot be read.
        """
