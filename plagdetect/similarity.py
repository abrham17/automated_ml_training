from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import combinations
from multiprocessing import Pool
from typing import Dict, Iterable, List, Sequence, Tuple

from .types import Document


def _tokenize(text: str, unit: str) -> List[str]:
    if unit == "word":
        return text.split()
    if unit == "char":
        return list(text)
    raise ValueError(f"Unknown unit: {unit}")


def _shingles(tokens: Sequence[str], k: int) -> List[Tuple[str, ...]]:
    if k <= 0 or len(tokens) < k:
        return []
    return [tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)]


def _hash_tuple(t: Tuple[str, ...]) -> int:
    h = hashlib.sha1("\x1f".join(t).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big", signed=False)


def _winnow(hashes: List[int], window_size: int) -> List[Tuple[int, int]]:
    # Returns list of (hash, position) fingerprints following winnowing algorithm
    if window_size <= 0 or len(hashes) < window_size:
        return [(h, i) for i, h in enumerate(hashes)]
    fingerprints: List[Tuple[int, int]] = []
    last_min_pos = -1
    for i in range(0, len(hashes) - window_size + 1):
        window = hashes[i : i + window_size]
        min_hash = min(window)
        min_pos = i + window.index(min_hash)
        if min_pos != last_min_pos:
            fingerprints.append((min_hash, min_pos))
            last_min_pos = min_pos
    return fingerprints


def _doc_fingerprints(doc: Document, *, k_gram: int, unit: str, use_winnowing: bool, window_size: int):
    tokens = _tokenize(doc.content, unit)
    shingles = _shingles(tokens, k_gram)
    hashes = [_hash_tuple(s) for s in shingles]
    if use_winnowing:
        fps = _winnow(hashes, window_size)
        signature = {h for h, _ in fps}
    else:
        signature = set(hashes)
    return signature


def _jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _compare_pair(args):
    (doc_a, sig_a), (doc_b, sig_b), method = args
    sim = _jaccard(sig_a, sig_b)
    return {
        "doc_a": doc_a.doc_id,
        "doc_b": doc_b.doc_id,
        "similarity": sim,
        "method": method,
        "overlap": len(sig_a & sig_b),
    }


def pairwise_compare(
    documents: Sequence[Document],
    *,
    k_gram: int,
    unit: str,
    use_winnowing: bool,
    window_size: int,
    threshold: float,
    num_workers: int,
) -> List[Dict]:
    method = f"winnow(k={k_gram},t={window_size},unit={unit})" if use_winnowing else f"shingle(k={k_gram},unit={unit})"
    signatures = [
        (doc, _doc_fingerprints(doc, k_gram=k_gram, unit=unit, use_winnowing=use_winnowing, window_size=window_size))
        for doc in documents
    ]

    pairs = list(combinations(signatures, 2))
    if not pairs:
        return []

    if num_workers and num_workers > 1:
        with Pool(processes=num_workers) as pool:
            results = pool.map(_compare_pair, [((a_doc, a_sig), (b_doc, b_sig), method) for (a_doc, a_sig), (b_doc, b_sig) in pairs])
    else:
        results = [_compare_pair(((a_doc, a_sig), (b_doc, b_sig), method)) for (a_doc, a_sig), (b_doc, b_sig) in pairs]

    return [r for r in results if r["similarity"] >= threshold]

