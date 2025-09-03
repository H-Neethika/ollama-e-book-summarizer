from __future__ import annotations

from pathlib import Path

from src.pipeline.manifest import compute_run_id, sha256_text


def test_compute_run_id_deterministic():
    a = compute_run_id("book", "0123456789abcdef", "gemma:2b", "bnotes")
    b = compute_run_id("book", "0123456789abcdef", "gemma:2b", "bnotes")
    assert a == b
    assert a.startswith("book-")

