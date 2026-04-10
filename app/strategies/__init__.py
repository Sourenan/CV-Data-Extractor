"""
Strategies sub-package.

Each module implements one ExtractionStrategy variant.
"""

from app.strategies.gemini_name_strategy import GeminiNameStrategy, LLMClient
from app.strategies.regex_email_strategy import RegexEmailStrategy
from app.strategies.rule_based_skills_strategy import RuleBasedSkillsStrategy

__all__ = [
    "RegexEmailStrategy",
    "GeminiNameStrategy",
    "LLMClient",
    "RuleBasedSkillsStrategy",
]
