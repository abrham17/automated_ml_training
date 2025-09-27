from __future__ import annotations

import csv
import json
from functools import partial
from multiprocessing import cpu_count
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from .io_utils import collect_files, read_text
from .normalize import normalize_code
from .similarity import pairwise_compare
from .types import Document


 


def _write_report_json(output_path: Path, matches: List[Dict]) -> Dict:
    payload = {"matches": matches}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _write_report_csv(output_path: Path, matches: List[Dict]) -> Dict:
    fieldnames = ["doc_a", "doc_b", "similarity", "method", "overlap"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in matches:
            writer.writerow({k: row.get(k) for k in fieldnames})
    return {"path": str(output_path)}


def _write_report_html(output_path: Path, matches: List[Dict]) -> Dict:
    # Minimal HTML summary with table
    rows = "\n".join(
        f"<tr><td>{m['doc_a']}</td><td>{m['doc_b']}</td><td>{m['similarity']:.3f}</td><td>{m['method']}</td><td>{m.get('overlap','')}</td></tr>"
        for m in matches
    )
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'/>
  <title>plagdetect report</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f4f4f4; }}
  </style>
  </head>
  <body>
    <h1>Similarity Matches</h1>
    <table>
      <thead><tr><th>Doc A</th><th>Doc B</th><th>Similarity</th><th>Method</th><th>Overlap</th></tr></thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
    return {"path": str(output_path)}


def run_detection(
    *,
    inputs: Sequence[Path],
    include_globs: Sequence[str],
    exclude_globs: Sequence[str],
    strip_comments: bool,
    k_gram: int,
    unit: str,
    use_winnowing: bool,
    window_size: int,
    threshold: float,
    report_format: str,
    output_path: Path,
    num_workers: int,
):
    files = collect_files(inputs, include_globs, exclude_globs)
    documents: List[Document] = []
    for f in files:
        raw = read_text(f)
        norm = normalize_code(raw, path=f, strip_comments=strip_comments)
        documents.append(Document(doc_id=str(f), path=f, content=norm))

    matches = pairwise_compare(
        documents,
        k_gram=k_gram,
        unit=unit,
        use_winnowing=use_winnowing,
        window_size=window_size,
        threshold=threshold,
        num_workers=num_workers if num_workers > 0 else cpu_count(),
    )

    if report_format == "json":
        return _write_report_json(output_path, matches)
    if report_format == "csv":
        return _write_report_csv(output_path, matches)
    if report_format == "html":
        return _write_report_html(output_path, matches)
    raise ValueError(f"Unknown report format: {report_format}")

