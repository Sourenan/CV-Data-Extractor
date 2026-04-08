"""
Rule-based skills extraction strategy.

Matches skills against a configurable catalog using case-insensitive
whole-word search.  Returns display values from the catalog (not the
casing found in the resume) so the output list is clean and consistent.

A sensible default catalog is provided so the class is useful out of
the box, but callers can supply their own list for domain-specific needs.
"""

from __future__ import annotations

import re

from app.extractors.base import ExtractionStrategy

# ---------------------------------------------------------------------------
# Default skill catalog
# ---------------------------------------------------------------------------

DEFAULT_SKILL_CATALOG: list[str] = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#",
    "Go", "Rust", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Bash", "Shell", "PowerShell", "SQL", "HTML", "CSS",
    # Frameworks & libraries
    "Django", "Flask", "FastAPI", "Spring", "React", "Angular", "Vue",
    "Node.js", "Express", "Next.js", "NumPy", "Pandas", "Scikit-learn",
    "TensorFlow", "PyTorch", "Keras", "Hugging Face", "LangChain",
    # Data & ML
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "LLM", "RAG", "Fine-tuning", "Data Analysis", "Data Engineering",
    "Feature Engineering", "Model Deployment",
    # Cloud & infra
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "CI/CD", "GitHub Actions", "Jenkins",
    # Databases
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "DynamoDB", "BigQuery",
    # Practices
    "REST", "GraphQL", "gRPC", "Microservices", "Agile", "Scrum",
    "TDD", "OOP", "Design Patterns", "Git",
]


class RuleBasedSkillsStrategy(ExtractionStrategy[list[str]]):
    """Extracts skills by matching against a configurable skill catalog.

    Parameters
    ----------
    catalog:
        List of canonical skill names to search for.  Defaults to
        ``DEFAULT_SKILL_CATALOG`` when not supplied.
    """

    def __init__(self, catalog: list[str] | None = None) -> None:
        self._catalog = catalog if catalog is not None else DEFAULT_SKILL_CATALOG
        # Pre-compile one pattern per skill for efficiency
        self._patterns: list[tuple[str, re.Pattern[str]]] = [
            (skill, re.compile(rf"\b{re.escape(skill)}\b", re.IGNORECASE))
            for skill in self._catalog
        ]

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
