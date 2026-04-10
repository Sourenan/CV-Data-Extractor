"""
Tests for ResumeExtractor.
"""

from unittest.mock import MagicMock

from app.models import ResumeData
from app.services.resume_extractor import ResumeExtractor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_extractor(return_value):
    """Return a FieldExtractor mock that returns *return_value* on extract()."""
    m = MagicMock()
    m.extract.return_value = return_value
    return m


def _raising_extractor(exc: Exception):
    """Return a FieldExtractor mock whose extract() raises *exc*."""
    m = MagicMock()
    m.extract.side_effect = exc
    return m


RESUME_TEXT = "Jane Doe\njane@example.com\nPython Docker"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestResumeExtractor:
    def test_builds_resume_data_from_all_extractors(self):
        extractor = ResumeExtractor(
            extractors={
                "name": _mock_extractor("Jane Doe"),
                "email": _mock_extractor("jane@example.com"),
                "skills": _mock_extractor(["Python", "Docker"]),
            }
        )
        result = extractor.extract(RESUME_TEXT)

        assert isinstance(result, ResumeData)
        assert result.name == "Jane Doe"
        assert result.email == "jane@example.com"
        assert result.skills == ["Python", "Docker"]

    def test_missing_name_extractor_defaults_to_none(self):
        extractor = ResumeExtractor(
            extractors={
                "email": _mock_extractor("jane@example.com"),
                "skills": _mock_extractor(["Python"]),
            }
        )
        result = extractor.extract(RESUME_TEXT)
        assert result.name is None

    def test_missing_email_extractor_defaults_to_none(self):
        extractor = ResumeExtractor(
            extractors={
                "name": _mock_extractor("Jane Doe"),
                "skills": _mock_extractor(["Python"]),
            }
        )
        result = extractor.extract(RESUME_TEXT)
        assert result.email is None

    def test_missing_skills_extractor_defaults_to_empty_list(self):
        extractor = ResumeExtractor(
            extractors={
                "name": _mock_extractor("Jane Doe"),
                "email": _mock_extractor("jane@example.com"),
            }
        )
        result = extractor.extract(RESUME_TEXT)
        assert result.skills == []

    def test_empty_extractor_dict_returns_all_defaults(self):
        extractor = ResumeExtractor(extractors={})
        result = extractor.extract(RESUME_TEXT)
        assert result == ResumeData(name=None, email=None, skills=[])

    def test_raising_name_extractor_does_not_crash_pipeline(self):
        """A failing name extractor should not prevent email/skills extraction."""
        extractor = ResumeExtractor(
            extractors={
                "name": _raising_extractor(RuntimeError("LLM timeout")),
                "email": _mock_extractor("jane@example.com"),
                "skills": _mock_extractor(["Python"]),
            }
        )
        result = extractor.extract(RESUME_TEXT)

        assert result.name is None  # fallen back to default
        assert result.email == "jane@example.com"
        assert result.skills == ["Python"]

    def test_raising_skills_extractor_falls_back_to_empty_list(self):
        extractor = ResumeExtractor(
            extractors={
                "name": _mock_extractor("Jane Doe"),
                "email": _mock_extractor("jane@example.com"),
                "skills": _raising_extractor(ValueError("bad catalog")),
            }
        )
        result = extractor.extract(RESUME_TEXT)
        assert result.skills == []

    def test_all_extractors_receive_the_same_text(self):
        name_mock = _mock_extractor("Jane Doe")
        email_mock = _mock_extractor("jane@example.com")
        skills_mock = _mock_extractor([])

        extractor = ResumeExtractor(
            extractors={
                "name": name_mock,
                "email": email_mock,
                "skills": skills_mock,
            }
        )
        extractor.extract(RESUME_TEXT)

        name_mock.extract.assert_called_once_with(RESUME_TEXT)
        email_mock.extract.assert_called_once_with(RESUME_TEXT)
        skills_mock.extract.assert_called_once_with(RESUME_TEXT)

    def test_empty_text_is_passed_through_to_extractors(self):
        name_mock = _mock_extractor(None)
        extractor = ResumeExtractor(extractors={"name": name_mock})
        extractor.extract("")
        name_mock.extract.assert_called_once_with("")
