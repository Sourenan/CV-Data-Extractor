"""
ResumeParserFramework — top-level entry point for the framework.

This class is the single object a caller needs to interact with.
It combines a :class:`~app.parsers.base.FileParser` (file → text) with
a :class:`~app.services.resume_extractor.ResumeExtractor` (text → data)
and exposes one public method: :meth:`parse_resume`.
"""

from __future__ import annotations

from app.models import ResumeData
from app.parsers.base import FileParser
from app.services.resume_extractor import ResumeExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResumeParserFramework:
    """Combines a file parser and a field-extraction coordinator.

    Both dependencies are supplied at construction time (constructor
    injection), which keeps the class format-agnostic and trivially
    testable — pass a stub parser and a stub extractor and the
    framework behaves identically without touching the filesystem or
    any external API.

    Parameters
    ----------
    file_parser:
        Any concrete ``FileParser`` (``PDFParser``, ``WordParser``, …).
        The framework does not inspect the file extension; callers are
        responsible for passing the correct parser for the given file.
    resume_extractor:
        A configured ``ResumeExtractor`` instance holding the desired
        field extractors and strategies.

    Example
    -------
    ::

        framework = ResumeParserFramework(
            file_parser=PDFParser(),
            resume_extractor=ResumeExtractor({
                "name":   NameExtractor(GeminiNameStrategy.from_api_key(api_key)),
                "email":  EmailExtractor(RegexEmailStrategy()),
                "skills": SkillsExtractor(RuleBasedSkillsStrategy()),
            }),
        )
        result = framework.parse_resume("resume.pdf")
    """

    def __init__(
        self,
        file_parser: FileParser,
        resume_extractor: ResumeExtractor,
    ) -> None:
        self._parser = file_parser
        self._extractor = resume_extractor

    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse a resume file and return its structured data.

        Parameters
        ----------
        file_path:
            Path to a resume file.  The file extension is expected to
            match the ``FileParser`` passed at construction time.

        Returns
        -------
        ResumeData
            Structured data with ``name``, ``email``, and ``skills``.

        Raises
        ------
        FileParsingError
            Propagated from the parser if the file cannot be read.
        """
        logger.info("Parsing resume: %s", file_path)
        text = self._parser.parse(file_path)
        return self._extractor.extract(text)
