"""MATH-500 loader: fetch once, cache locally, load a (sub)set. Standalone — no HF deps."""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path

_URL = "https://huggingface.co/datasets/HuggingFaceH4/MATH-500/resolve/main/test.jsonl"
_CACHE = Path(__file__).resolve().parent.parent / "data" / "math500.jsonl"


@dataclass
class Problem:
    problem: str
    answer: str


def _fetch(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(_URL, headers={"User-Agent": "paretothink/0.0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:  # follows HF redirect
        dest.write_bytes(r.read())


def load_math500(limit: int | None = None, cache_path: Path = _CACHE) -> list[Problem]:
    cache_path = Path(cache_path)
    if not cache_path.exists():
        _fetch(cache_path)
    problems = []
    for line in cache_path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            problems.append(Problem(row["problem"], str(row["answer"])))
    return problems[:limit] if limit else problems
