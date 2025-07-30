# Speak2Py

**Version:** MVP v0.1

## Overview

Speak2Py is a Python library designed to let you load and manipulate pandas DataFrames through simple English-like commands. This initial MVP focuses on robust, minimal file ingestion.

---

## MVP Features (v0.1)

1. **Basic File Loader**

   - Detects file type by extension (`.csv`, `.xls`, `.xlsx`, `.json`)
   - Returns a `pandas.DataFrame`

2. **Unit Tests**

   - Verifies CSV, Excel, and JSON loading
   - Ensures shape and data integrity

3. **Packaging Structure**

   - `src/speak2py/file_reader.py` with `load_data(path)`
   - `tests/test_file_reader.py` for pytest

---

## Installation

```bash
pip install speak2py
```

## Quickstart

```python
from speak2py.file_reader import load_data

df = load_data("data.csv")  # CSV, Excel, or JSON
print(df.head())
```

---

## MVP v0.1 Description

- **Purpose:** Provide a minimal, reliable entry point for loading tabular data into pandas.
- **What’s Included:**

  - `load_data(path: str) -> pd.DataFrame`
  - Extension-based loader for CSV, Excel, JSON
  - Basic unit tests

- **Why It Matters:** Lays the foundation for adding natural-language parsing and AI-driven commands in later releases.

---

## Next Steps

1. **Natural Language Parser**

   - Implement `speak2py("read the file data.csv")` entry point

2. **Additional Formats**

   - Add Parquet, SQL, and other file types

3. **AI Integration**

   - Hook in a basic parser for mapping English to function calls

4. **CLI & Plugin**

   - Expose a command-line interface and package as a VS Code plugin

---

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT © 2025 Speak2Py Contributors
