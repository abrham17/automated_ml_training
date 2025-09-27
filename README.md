PlagDetect
==========

CLI tool to detect similarities between student assignments/projects using normalization, shingling, and winnowing.

Install (editable)
------------------

```bash
pip install -e .
```

Usage
-----

```bash
plagdetect path/to/submissions \
  --include-glob "**/*.py" \
  --strip-comments \
  --k-gram 5 \
  --unit word \
  --winnow \
  --window 4 \
  --threshold 0.6 \
  --report json \
  --output report.json
```

- inputs can be files and/or directories. Multiple paths allowed.
- use `--include-glob` multiple times to include extensions (e.g., `**/*.py`, `**/*.java`).
- default excludes: `**/.git/**`, `**/node_modules/**`, `**/__pycache__/**`.

Reports
-------

- json: writes `{"matches": [...]}` and echoes to stdout
- csv: writes a CSV with columns: doc_a, doc_b, similarity, method, overlap
- html: simple table for quick review

Similarity Methods
------------------

- Shingling: Jaccard similarity over k-gram hashes (word or char units)
- Winnowing: Document fingerprints via minimum hash in sliding windows

Notes
-----

- Comment stripping is heuristic and language-agnostic; for robust results, prefer language-specific parsers.
- Adjust `--k-gram` and `--window` based on language and assignment size.

Web App
-------

Install extra deps, then run:

```bash
python3 -m pip install --break-system-packages "uvicorn[standard]" fastapi
$HOME/.local/bin/plagdetect-web --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` and upload files to analyze.

