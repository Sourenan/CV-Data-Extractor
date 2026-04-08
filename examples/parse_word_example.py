"""
Example: Parse a Word (.docx) resume using the full framework.

To use a real Gemini model, replace the stub client with:

    import os
    strategy = GeminiNameStrategy.from_api_key(os.environ["GEMINI_API_KEY"])

Never hard-code your API key in source code.
"""

import json
import sys

from app.extractors.email_extractor import EmailExtractor
from app.extractors.name_extractor import NameExtractor
from app.extractors.skills_extractor import SkillsExtractor
from app.framework import ResumeParserFramework
from app.parsers.word_parser import WordParser
from app.services.resume_extractor import ResumeExtractor
from app.strategies.gemini_name_strategy import GeminiNameStrategy
from app.strategies.regex_email_strategy import RegexEmailStrategy
from app.strategies.rule_based_skills_strategy import RuleBasedSkillsStrategy


# ---------------------------------------------------------------------------
# Stub Gemini client — safe for demos and public repos.
# Replace with GeminiNameStrategy.from_api_key(...) in production.
# ---------------------------------------------------------------------------

class _StubLLMClient:
    """Returns a placeholder name so the example runs without an API key."""

    def generate_content(self, prompt: str) -> object:
        class _Response:
            text = "Jane Doe"  # placeholder

        return _Response()


# ---------------------------------------------------------------------------
# Build the framework
# ---------------------------------------------------------------------------

framework = ResumeParserFramework(
    file_parser=WordParser(),
    resume_extractor=ResumeExtractor(
        extractors={
            "name": NameExtractor(strategy=GeminiNameStrategy(client=_StubLLMClient())),
            "email": EmailExtractor(strategy=RegexEmailStrategy()),
            "skills": SkillsExtractor(strategy=RuleBasedSkillsStrategy()),
        }
    ),
)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examples/parse_word_example.py <path/to/resume.docx>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = framework.parse_resume(file_path)

    print(json.dumps(
        {"name": result.name, "email": result.email, "skills": result.skills},
        indent=2,
    ))
