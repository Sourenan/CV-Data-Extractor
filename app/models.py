"""
Domain model for extracted resume data.
"""

from dataclasses import dataclass, field


@dataclass
class ResumeData:
    """Encapsulates the three structured fields extracted from a resume."""

    name: str | None = None
    email: str | None = None
    skills: list[str] = field(default_factory=list)
