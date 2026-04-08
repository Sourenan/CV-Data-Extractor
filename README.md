# CV Data Extractor

A pluggable resume parsing framework in Python that extracts structured information from PDF and Word resumes. Built as a technical assignment demonstrating Object-Oriented Design principles: clean abstractions, separation of concerns, and fully swappable extraction strategies.

## Output

Every resume produces a single JSON-serialisable object:

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@gmail.com",
  "skills": ["Python", "Machine Learning", "Docker"]
}
```

---

## Architecture

```
ResumeParserFramework
├── FileParser           (abstract)
│   ├── PDFParser        → PyMuPDF
│   └── WordParser       → python-docx
└── ResumeExtractor      (takes a dict of FieldExtractors)
    ├── NameExtractor    → GeminiNameStrategy     (LLM-based)
    ├── EmailExtractor   → RegexEmailStrategy      (regex)
    └── SkillsExtractor  → RuleBasedSkillsStrategy (catalog)
```

The key design decision is separating **what** to extract (`FieldExtractor`) from **how** to extract it (`ExtractionStrategy`). Both are injected at wiring time, so any strategy can be swapped — for any field, for any reason — without modifying any other class.

---

## Project Structure

```
app/
├── models.py                        # ResumeData dataclass
├── exceptions.py                    # Custom exceptions
├── framework.py                     # ResumeParserFramework
├── parsers/
│   ├── base.py                      # FileParser ABC
│   ├── pdf_parser.py
│   └── word_parser.py
├── extractors/
│   ├── base.py                      # FieldExtractor[T] + ExtractionStrategy[T] ABCs
│   ├── name_extractor.py
│   ├── email_extractor.py
│   └── skills_extractor.py
├── strategies/
│   ├── gemini_name_strategy.py      # LLM-based name extraction
│   ├── regex_email_strategy.py
│   └── rule_based_skills_strategy.py
├── services/
│   └── resume_extractor.py          # ResumeExtractor coordinator
└── utils/
    ├── logger.py
    └── text_utils.py
examples/
├── parse_pdf_example.py
└── parse_word_example.py
tests/                               # 64 pytest tests, all passing
```

---

## Why it is pluggable

- **File format** — pass `PDFParser()` or `WordParser()` to `ResumeParserFramework`. Adding a new format means writing one class and passing it in.
- **Extraction technique** — pass any `ExtractionStrategy` to any `FieldExtractor`. Switch from regex to NER for email by passing a different object; nothing else changes.
- **Field set** — `ResumeExtractor` receives a plain `dict`. Adding a new field means adding a key; removing one means omitting it.

---

## Extraction strategy choices

| Field | Strategy | Rationale |
|---|---|---|
| Name | `GeminiNameStrategy` (LLM) | Names are highly varied and resist simple rules; an LLM handles international names, titles, and unusual formats |
| Email | `RegexEmailStrategy` | Email format is well-defined; a single regex is accurate, fast, and zero-cost |
| Skills | `RuleBasedSkillsStrategy` | A curated catalog is deterministic, fast, and easy to extend for domain-specific skill sets |

---

## Setup

**Python 3.10+ required.**

```bash
pip install -r requirements.txt
```

### LLM configuration

The `GeminiNameStrategy` requires a Gemini API client. Set your API key as an environment variable — never commit it:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Then wire it in code:

```python
import os
from app.strategies.gemini_name_strategy import GeminiNameStrategy

strategy = GeminiNameStrategy.from_api_key(os.environ["GEMINI_API_KEY"])
```

The examples use a safe stub client so they run without any API key.

---

## Running the examples

```bash
# PDF
python examples/parse_pdf_example.py path/to/resume.pdf

# Word
python examples/parse_word_example.py path/to/resume.docx
```

---

## Running the tests

```bash
pytest tests/ -v
```

64 tests covering happy paths, edge cases, and failure modes. All LLM calls are mocked — no API key required.

---

## Assumptions

- The file extension accurately reflects the file type (`.pdf` → PDF, `.docx` → Word).
- Skills extraction accuracy is not the focus; the catalog can be extended freely.
- Only the first email address found in the resume is returned.
- The Gemini model is available and the caller manages API key rotation.

---

## Edge cases handled

- Missing or non-existent file → `FileParsingError`
- Corrupt or unreadable file → `FileParsingError` with descriptive message
- Empty document / no extractable text → empty string passed to extractors, which return safe defaults
- LLM timeout or API error → `name` returns `None`; email and skills are unaffected
- One extractor failing does not crash the pipeline — all other fields still extract
- Skills deduplication across casing variants (`python`, `Python`, `PYTHON` → one entry)
- Skills in Word document tables are included alongside paragraph text

---

## Limitations

- `RuleBasedSkillsStrategy` only finds skills explicitly listed in the catalog.
- PDFs that are scanned images (no selectable text) will produce an empty string; OCR is out of scope.
- Only `.pdf` and `.docx` formats are supported out of the box.
- The framework extracts the first occurrence of an email address; resumes with multiple emails only return one.

---

## Future improvements

- Add a `ParserFactory` that selects the correct parser based on file extension.
- Implement an NER-based name strategy as an alternative to the LLM.
- Add confidence scores to extracted fields.
- Support `.odt` and plain-text `.txt` resume formats.
- Extend `RuleBasedSkillsStrategy` to load catalogs from external files or APIs.
