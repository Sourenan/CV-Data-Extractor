# CV Data Extractor

A pluggable Resume Parsing framework in Python that extracts structured information from resumes in PDF and Word Document formats.

## Overview

This framework is designed around **Object-Oriented Design** principles — separation of concerns, composition over inheritance, and pluggable extraction strategies. It extracts three fields from any resume:

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@gmail.com",
  "skills": ["Python", "Machine Learning", "LLM"]
}
```

## Architecture

```
ResumeParserFramework
├── FileParser  (abstract)
│   ├── PDFParser
│   └── WordParser
└── ResumeExtractor  (takes a dict of FieldExtractors)
    ├── NameExtractor      → GeminiNameStrategy     (LLM-based)
    ├── EmailExtractor     → RegexEmailStrategy      (regex-based)
    └── SkillsExtractor    → RuleBasedSkillsStrategy (catalog-based)
```

Each `FieldExtractor` delegates to an interchangeable `ExtractionStrategy`, making it easy to swap strategies without changing the extractor or the coordinator.

## Project Structure

```
cv_data_extractor/
├── __init__.py
├── exceptions.py            # Custom exceptions
├── models.py                # ResumeData dataclass
├── parsers/
│   ├── __init__.py
│   ├── base.py              # FileParser ABC
│   ├── pdf_parser.py        # PDFParser
│   └── word_parser.py       # WordParser
├── extractors/
│   ├── __init__.py
│   ├── base.py              # FieldExtractor ABC + ExtractionStrategy ABC
│   ├── name_extractor.py    # NameExtractor + GeminiNameStrategy
│   ├── email_extractor.py   # EmailExtractor + RegexEmailStrategy
│   └── skills_extractor.py  # SkillsExtractor + RuleBasedSkillsStrategy
├── resume_extractor.py      # ResumeExtractor coordinator
└── framework.py             # ResumeParserFramework
tests/
├── __init__.py
├── test_parsers.py
├── test_extractors.py
├── test_resume_extractor.py
└── test_framework.py
examples/
├── parse_pdf_resume.py
└── parse_word_resume.py
requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

The LLM-based name extractor uses the [Google Gemini API](https://ai.google.dev/). Set your API key as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

> **Never commit your API key.** The framework reads it from the environment at runtime.

## Usage

### Parse a PDF resume

```python
from cv_data_extractor.parsers.pdf_parser import PDFParser
from cv_data_extractor.extractors.name_extractor import NameExtractor, GeminiNameStrategy
from cv_data_extractor.extractors.email_extractor import EmailExtractor, RegexEmailStrategy
from cv_data_extractor.extractors.skills_extractor import SkillsExtractor, RuleBasedSkillsStrategy
from cv_data_extractor.resume_extractor import ResumeExtractor
from cv_data_extractor.framework import ResumeParserFramework

framework = ResumeParserFramework(
    file_parser=PDFParser(),
    resume_extractor=ResumeExtractor(
        extractors={
            "name": NameExtractor(GeminiNameStrategy()),
            "email": EmailExtractor(RegexEmailStrategy()),
            "skills": SkillsExtractor(RuleBasedSkillsStrategy()),
        }
    ),
)

result = framework.parse_resume("path/to/resume.pdf")
print(result)
```

### Parse a Word resume

```python
from cv_data_extractor.parsers.word_parser import WordParser
# ... same extractor setup as above ...

framework = ResumeParserFramework(
    file_parser=WordParser(),
    resume_extractor=ResumeExtractor(...),
)

result = framework.parse_resume("path/to/resume.docx")
print(result)
```

See the [`examples/`](examples/) directory for complete runnable scripts.

## Running Tests

```bash
pytest
```

All tests are deterministic. LLM calls are fully mocked.

## Design Decisions

| Decision | Rationale |
|---|---|
| `ExtractionStrategy` abstraction | Decouples *what* to extract from *how* to extract it; strategies can be swapped without touching extractors |
| `FieldExtractor` wraps a strategy | Gives each field its own class (meeting the assignment contract) while keeping the extractor thin |
| `ResumeExtractor` takes a plain `dict` | Simple and explicit; no magic registration or decorator-based plugins needed at this scale |
| Constructor injection for `FileParser` | Keeps `ResumeParserFramework` testable and format-agnostic |
| LLM for name extraction | Names are highly varied and resist regex; an LLM produces the most robust results |
| Regex for email | Email format is well-defined by RFC 5322 and does not warrant an LLM call |
| Rule-based catalog for skills | Fast, deterministic, and easily extended by updating the catalog |

## Requirements

- Python 3.10+
- `pdfplumber` — PDF text extraction
- `python-docx` — Word document parsing
- `google-generativeai` — Gemini LLM API
- `pytest` — testing
