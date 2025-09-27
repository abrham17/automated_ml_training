from __future__ import annotations

import re
from pathlib import Path


_whitespace_re = re.compile(r"\s+")


def _strip_comments_generic(text: str) -> str:
    # Remove C/Java/JS style block and line comments
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//.*", " ", text)
    # Remove Python style comments
    text = re.sub(r"(^|\s)#.*", " ", text)
    return text


def normalize_code(text: str, *, path: Path | None = None, strip_comments: bool = False) -> str:
    processed = text
    if strip_comments:
        processed = _strip_comments_generic(processed)
    # Normalize whitespace and case
    processed = processed.lower()
    processed = _whitespace_re.sub(" ", processed).strip()
    return processed

