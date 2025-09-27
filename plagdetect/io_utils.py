from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable, List, Sequence, Set


def collect_files(inputs: Sequence[Path], include_globs: Sequence[str], exclude_globs: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    include_patterns = list(include_globs) or ["*"]
    exclude_patterns = list(exclude_globs)

    def is_included(path: Path) -> bool:
        name = str(path)
        inc = any(fnmatch.fnmatch(name, pat) for pat in include_patterns)
        exc = any(fnmatch.fnmatch(name, pat) for pat in exclude_patterns)
        return inc and not exc

    for inp in inputs:
        p = inp if isinstance(inp, Path) else Path(inp)
        if p.is_dir():
            for sub in p.rglob("*"):
                if sub.is_file() and is_included(sub):
                    files.append(sub)
        elif p.is_file():
            if is_included(p):
                files.append(p)
    # Deduplicate while preserving order
    seen: Set[str] = set()
    result: List[Path] = []
    for f in files:
        s = str(f.resolve())
        if s not in seen:
            seen.add(s)
            result.append(Path(s))
    return result


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1
        return path.read_text(encoding="latin-1")

