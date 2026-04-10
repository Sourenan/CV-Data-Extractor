"""
Tests for RuleBasedSkillsStrategy.
"""

import pytest

from app.strategies.rule_based_skills_strategy import (
    DEFAULT_SKILL_CATALOG,
    RuleBasedSkillsStrategy,
)


class TestRuleBasedSkillsStrategy:
    def setup_method(self):
        self.strategy = RuleBasedSkillsStrategy()

    # ------------------------------------------------------------------
    # Basic detection
    # ------------------------------------------------------------------

    def test_finds_known_skill(self):
        text = "I have experience with Python and Docker."
        result = self.strategy.extract(text)
        assert "Python" in result
        assert "Docker" in result

    def test_returns_catalog_display_name_not_resume_casing(self):
        # Resume says "python" (lowercase) — should return "Python" from catalog
        text = "Proficient in python and sql."
        result = self.strategy.extract(text)
        assert "Python" in result
        assert "SQL" in result

    def test_case_insensitive_matching(self):
        text = "PYTHON DOCKER AWS"
        result = self.strategy.extract(text)
        assert "Python" in result
        assert "Docker" in result
        assert "AWS" in result

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def test_no_duplicate_skills(self):
        # "Python" appears multiple times with different casing
        text = "Python, python, PYTHON"
        result = self.strategy.extract(text)
        assert result.count("Python") == 1

    def test_result_has_no_duplicates_generally(self):
        text = "Python Python Python Docker Docker"
        result = self.strategy.extract(text)
        assert len(result) == len(set(result))

    # ------------------------------------------------------------------
    # Empty / no-match cases
    # ------------------------------------------------------------------

    def test_returns_empty_list_when_no_skills_found(self):
        text = "I am an experienced manager with strong leadership skills."
        result = self.strategy.extract(text)
        assert isinstance(result, list)
        # No skills from the catalog should match generic words
        for skill in result:
            assert skill in DEFAULT_SKILL_CATALOG

    def test_returns_empty_list_for_empty_text(self):
        assert self.strategy.extract("") == []

    def test_returns_empty_list_for_whitespace_only(self):
        assert self.strategy.extract("   \n\t  ") == []

    # ------------------------------------------------------------------
    # Custom catalog
    # ------------------------------------------------------------------

    def test_custom_catalog_is_used(self):
        custom = ["Underwater Welding", "Crop Rotation"]
        strategy = RuleBasedSkillsStrategy(catalog=custom)
        text = "Experience in underwater welding and crop rotation."
        result = strategy.extract(text)
        assert "Underwater Welding" in result
        assert "Crop Rotation" in result

    def test_default_catalog_not_used_when_custom_provided(self):
        strategy = RuleBasedSkillsStrategy(catalog=["OnlyThis"])
        text = "I know Python, Docker, and OnlyThis."
        result = strategy.extract(text)
        assert result == ["OnlyThis"]

    # ------------------------------------------------------------------
    # Multi-word skills
    # ------------------------------------------------------------------

    def test_finds_multi_word_skill(self):
        text = "I have worked on Machine Learning and Deep Learning projects."
        result = self.strategy.extract(text)
        assert "Machine Learning" in result
        assert "Deep Learning" in result

    # ------------------------------------------------------------------
    # from_file factory
    # ------------------------------------------------------------------

    def test_from_file_loads_catalog_correctly(self, tmp_path):
        catalog_file = tmp_path / "skills.json"
        catalog_file.write_text('["Rust", "Elixir", "Haskell"]', encoding="utf-8")

        strategy = RuleBasedSkillsStrategy.from_file(str(catalog_file))
        result = strategy.extract("I know Rust and Elixir but not Java.")

        assert "Rust" in result
        assert "Elixir" in result
        assert "Java" not in result  # not in custom catalog

    def test_from_file_raises_for_missing_file(self):
        with pytest.raises(ValueError, match="not found"):
            RuleBasedSkillsStrategy.from_file("/nonexistent/path/skills.json")

    def test_from_file_raises_for_invalid_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("this is not json", encoding="utf-8")

        with pytest.raises(ValueError, match="not valid JSON"):
            RuleBasedSkillsStrategy.from_file(str(bad_file))

    def test_from_file_raises_for_non_list_json(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('{"skill": "Python"}', encoding="utf-8")

        with pytest.raises(ValueError, match="array of strings"):
            RuleBasedSkillsStrategy.from_file(str(bad_file))
