# DevTrace AI 🔍

An autonomous software debugging, code understanding, and verification assistant for Python projects.

DevTrace AI scans existing codebases, extracts structural dependencies using Python's Abstract Syntax Tree (AST), localizes bugs, generates intelligent fixes using LLM reasoning, and autonomously runs test suites (`pytest`) to verify fixes in a closed feedback loop.

---

## 🚀 Key Highlights

- **AST-Powered Code Understanding:** Deterministically extracts functions, classes, imports, and call dependencies without relying purely on fuzzy token matching.
- **Bug & Issue Localization:** Maps incoming bug reports or failing tests directly to the culprit source files and functions.
- **AI Patch Generation:** Employs LLM intelligence to craft minimal, targeted code fixes.
- **Autonomous Test Verification:** Executes `pytest` in real time to guarantee that the fix passes and prevents regressions.
- **Interactive Traceability:** Connects the complete development chain: `Issue ↔ Code ↔ Test ↔ Verified Patch`.

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI (Python)
- **Static Code Analysis:** Python `ast` module
- **AI Reasoning:** Google Gemini API
- **Test Automation:** Pytest
- **Dashboard / UI:** Streamlit
- **Version Control:** Git & GitHub

---

## 📁 Project Structure (In Progress)

```text
devtrace-ai/
├── backend/          # FastAPI backend services and endpoints
├── core/             # AST parser, localization, and patch engines
├── benchmarks/       # Curated mini test repositories for validation
├── ui/               # Streamlit interactive dashboard
├── tests/            # Test suite for DevTrace AI itself
├── .gitignore        # Git ignore rules
└── README.md         # Project documentation
```

---

## 👩‍💻 Author
- **Archita** ([@Archita-26](https://github.com/Archita-26))
