"""
Rule-based skills extraction strategy.

Matches skills against a configurable catalog using case-insensitive
whole-word search.  Returns display values from the catalog (not the
casing found in the resume) so the output list is clean and consistent.

The default catalog is loaded from ``data/default_skills.json`` (bundled
alongside this module) so no skill names are hard-coded in Python source.
Callers can supply their own catalog file via :meth:`RuleBasedSkillsStrategy.from_file`.
"""

from __future__ import annotations

import json
import pathlib
import re

from app.extractors.base import ExtractionStrategy

# ---------------------------------------------------------------------------
# Default skill catalog — loaded from the bundled JSON file so no skill
# names are hard-coded in Python source.  Edit data/default_skills.json
# to customise the defaults without touching any Python code.
# ---------------------------------------------------------------------------

_DEFAULT_CATALOG_PATH = pathlib.Path(__file__).parent / "data" / "default_skills.json"

try:
    with _DEFAULT_CATALOG_PATH.open(encoding="utf-8") as _fh:
        _raw = json.load(_fh)
except FileNotFoundError:
    raise RuntimeError(
        f"Default skill catalog not found: '{_DEFAULT_CATALOG_PATH}'. "
        "Ensure 'app/strategies/data/default_skills.json' is present in the repository."
    ) from None
except json.JSONDecodeError as _exc:
    raise RuntimeError(
        f"Default skill catalog is not valid JSON: '{_DEFAULT_CATALOG_PATH}' — {_exc}"
    ) from _exc

if not isinstance(_raw, list) or not all(isinstance(s, str) for s in _raw):
    raise RuntimeError(
        f"Default skill catalog must be a JSON array of strings: '{_DEFAULT_CATALOG_PATH}'"
    )

DEFAULT_SKILL_CATALOG: list[str] = _raw


class RuleBasedSkillsStrategy(ExtractionStrategy[list[str]]):
    """Extracts skills by matching against a configurable skill catalog.

    Parameters
    ----------
    catalog:
        List of canonical skill names to search for.  Defaults to
        ``DEFAULT_SKILL_CATALOG`` when not supplied.

    To load a catalog from an external file instead of hard-coding it,
    use the :meth:`from_file` classmethod::

        strategy = RuleBasedSkillsStrategy.from_file("skills_catalog.json")

    The JSON file should be a plain list of strings::

        ["Python", "Docker", "Kubernetes", "PostgreSQL"]
    """

    def __init__(self, catalog: list[str] | None = None) -> None:
        self._catalog = catalog if catalog is not None else DEFAULT_SKILL_CATALOG
        # Pre-compile one pattern per skill for efficiency
        self._patterns: list[tuple[str, re.Pattern[str]]] = [
            (skill, re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE))
            for skill in self._catalog
        ]

    @classmethod
    def from_file(cls, path: str) -> RuleBasedSkillsStrategy:
        """Load a skill catalog from a JSON file and return a new instance.

        The file must contain a JSON array of strings, e.g.::

            ["Python", "Docker", "Machine Learning"]

        This allows callers to supply a domain-specific catalog without
        modifying any source code — drop in a new file and point the
        strategy at it.

        Parameters
        ----------
        path:
            Path to a UTF-8 encoded JSON file containing a list of skill
            name strings.

        Returns
        -------
        RuleBasedSkillsStrategy
            A new instance configured with the catalog from *path*.

        Raises
        ------
        ValueError
            If the file cannot be read, is not valid JSON, or does not
            contain a list of strings.
        """
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            raise ValueError(f"Skill catalog file not found: '{path}'") from None
        except json.JSONDecodeError as exc:
            raise ValueError(f"Skill catalog file is not valid JSON: '{path}' — {exc}") from exc

        if not isinstance(data, list) or not all(isinstance(s, str) for s in data):
            raise ValueError(
                f"Skill catalog file must contain a JSON array of strings: '{path}'"
            )

        return cls(catalog=data)

    def extract(self, text: str) -> list[str]:
        if not text:
            return []

        seen: set[str] = set()
        results: list[str] = []

        for display_name, pattern in self._patterns:
            if pattern.search(text) and display_name not in seen:
                seen.add(display_name)
                results.append(display_name)

        return results
