"""
ResumeExtractor — orchestration coordinator for field extraction.
"""

from __future__ import annotations

from app.extractors.base import FieldExtractor
from app.models import ResumeData
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResumeExtractor:
    """Orchestrates extraction of all resume fields from plain text.

    Accepts a dictionary that maps field names to their ``FieldExtractor``
    instances.  Recognised keys are ``"name"``, ``"email"``, and
    ``"skills"``; any other keys are silently ignored.

    Each extractor is called independently so that a failure in one field
    never prevents the others from running.  Missing or failed fields fall
    back to safe defaults (``None`` / ``[]``).

    Parameters
    ----------
    extractors:
        A mapping of field name to ``FieldExtractor`` instance, e.g.::

            {
                "name":   NameExtractor(GeminiNameStrategy(...)),
                "email":  EmailExtractor(RegexEmailStrategy()),
                "skills": SkillsExtractor(RuleBasedSkillsStrategy()),
            }
    """

    def __init__(self, extractors: dict[str, FieldExtractor]) -> None:
        self._extractors = extractors

    def extract(self, text: str) -> ResumeData:
        """Run all registered extractors against *text* and return a
        :class:`~app.models.ResumeData` instance.

        Parameters
        ----------
        text:
            Plain-text content produced by a ``FileParser``.  May be an
            empty string — each extractor handles that safely.

        Returns
        -------
        ResumeData
            Fields that could not be extracted default to ``None`` (name,
            email) or ``[]`` (skills).
        """
        logger.info("Starting field extraction (text length: %d)", len(text))

        name = self._run("name", text, default=None)
        email = self._run("email", text, default=None)
        skills = self._run("skills", text, default=[])

        result = ResumeData(name=name, email=email, skills=skills)
        logger.info("Extraction complete: %s", result)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, field: str, text: str, *, default):
        """Call the extractor for *field* and return its result.

        Falls back to *default* if no extractor is registered for the
        field or if the extractor raises an unexpected exception.
        """
        extractor = self._extractors.get(field)
        if extractor is None:
            logger.debug("No extractor registered for field '%s', using default", field)
            return default

        try:
            value = extractor.extract(text)
            logger.debug("Field '%s' extracted: %r", field, value)
            return value
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Extractor for field '%s' raised an unexpected error: %s — "
                "falling back to default",
                field,
                exc,
            )
            return default
