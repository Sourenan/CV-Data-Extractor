"""
Example: Parse a Word (.docx) resume using the full framework.

Set the GEMINI_API_KEY environment variable before running:

    $env:GEMINI_API_KEY = "your-api-key"   # PowerShell
    export GEMINI_API_KEY="your-api-key"    # bash/zsh

Never hard-code your API key in source code.
"""

import json
import os
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
# Name strategy — uses real Gemini if GEMINI_API_KEY is set, stub otherwise.
# ---------------------------------------------------------------------------

_api_key = os.environ.get("GEMINI_API_KEY")

if _api_key:
    _name_strategy = GeminiNameStrategy.from_api_key(_api_key)
else:
    class _StubLLMClient:
        """Fallback when no API key is provided."""
        def generate_content(self, prompt: str) -> object:
            class _Response:
                text = "[set GEMINI_API_KEY to extract real name]"
            return _Response()

    _name_strategy = GeminiNameStrategy(client=_StubLLMClient())


# ---------------------------------------------------------------------------
# Build the framework
# ---------------------------------------------------------------------------

framework = ResumeParserFramework(
    parsers={".docx": WordParser()},
    resume_extractor=ResumeExtractor(
        extractors={
            "name": NameExtractor(strategy=_name_strategy),
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
