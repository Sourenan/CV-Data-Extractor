"""
ResumeParserFramework — top-level entry point for the framework.

This class is the single object a caller needs to interact with.
It accepts a registry of :class:`~app.parsers.base.FileParser` instances
keyed by file extension, and combines them with a
:class:`~app.services.resume_extractor.ResumeExtractor` (text → data).
It exposes one public method: :meth:`parse_resume`.
"""

from __future__ import annotations

import pathlib

from app.exceptions import UnsupportedFileTypeError
from app.models import ResumeData
from app.parsers.base import FileParser
from app.services.resume_extractor import ResumeExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResumeParserFramework:
    """Combines a registry of file parsers with a field-extraction coordinator.

    ``parse_resume`` inspects the file extension and automatically selects
    the correct parser, raising :class:`~app.exceptions.UnsupportedFileTypeError`
    if no parser is registered for that extension.

    Both dependencies are supplied at construction time (constructor
    injection), which keeps the class trivially testable — pass stub
    parsers and a stub extractor and the framework behaves identically
    without touching the filesystem or any external API.

    Parameters
    ----------
    parsers:
        A mapping of lowercase file extension (including the leading dot,
        e.g. ``".pdf"``, ``".docx"``) to a ``FileParser`` instance.
    resume_extractor:
        A configured ``ResumeExtractor`` instance holding the desired
        field extractors and strategies.

    Example
    -------
    ::

        framework = ResumeParserFramework(
            parsers={
                ".pdf":  PDFParser(),
                ".docx": WordParser(),
            },
            resume_extractor=ResumeExtractor({
                "name":   NameExtractor(GeminiNameStrategy.from_api_key(api_key)),
                "email":  EmailExtractor(RegexEmailStrategy()),
                "skills": SkillsExtractor(RuleBasedSkillsStrategy()),
            }),
        )
        result = framework.parse_resume("resume.pdf")   # uses PDFParser
        result = framework.parse_resume("resume.docx")  # uses WordParser
    """

    def __init__(
        self,
        parsers: dict[str, FileParser],
        resume_extractor: ResumeExtractor,
    ) -> None:
        self._parsers = parsers
        self._extractor = resume_extractor

    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse a resume file and return its structured data.

        The correct parser is selected automatically based on the file
        extension of *file_path*.

        Parameters
        ----------
        file_path:
            Path to a resume file.  The extension (e.g. ``.pdf``,
            ``.docx``) must match a key registered in ``parsers``.

        Returns
        -------
        ResumeData
            Structured data with ``name``, ``email``, and ``skills``.

        Raises
        ------
        UnsupportedFileTypeError
            If no parser is registered for the file's extension.
        FileParsingError
            Propagated from the parser if the file cannot be read.
        """
        logger.info("Parsing resume: %s", file_path)

        ext = pathlib.Path(file_path).suffix.lower()
        parser = self._parsers.get(ext)
        if parser is None:
            raise UnsupportedFileTypeError(ext)

        text = parser.parse(file_path)
        return self._extractor.extract(text)
