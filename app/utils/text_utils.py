"""
Small text normalisation helpers shared across parsers and extractors.
"""

import re


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace characters into a single space.

    Newlines are preserved as a single newline so that paragraph
    boundaries remain intact for downstream extractors.

    Parameters
    ----------
    text:
        Raw text, potentially containing tabs, multiple spaces, or
        carriage returns from PDF/Word extraction.

    Returns
    -------
    str
        Cleaned text with no leading/trailing whitespace.

    Examples
    --------
    >>> normalize_whitespace("  John   Doe\\n\\n  Python  ")
    'John Doe\\n\\nPython'
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of spaces/tabs on each line
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse more than two consecutive newlines into two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
