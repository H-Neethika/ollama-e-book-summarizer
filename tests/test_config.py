from __future__ import annotations

import os
from pathlib import Path

from src.pipeline.config import load_config


def test_load_config_defaults(tmp_path: Path, monkeypatch):
    # No env vars; use dev config file
    cfg = load_config(env="dev")
    assert cfg.env == "dev"
    assert isinstance(cfg.api_base, str)


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("EBOOKSUM_ENV", "dev")
    monkeypatch.setenv("EBOOKSUM_API_BASE", "http://example:11434/api")
    monkeypatch.setenv("EBOOKSUM_MODEL", "gemma:2b")
    monkeypatch.setenv("EBOOKSUM_PROMPT", "bnotes")
    monkeypatch.setenv("EBOOKSUM_OUTPUT_ROOT", "runs-test")
    monkeypatch.setenv("EBOOKSUM_CONTINUE", "1")
    monkeypatch.setenv("EBOOKSUM_VERBOSE", "true")

    cfg = load_config()
    assert cfg.api_base.endswith("/api")
    assert cfg.output_root == "runs-test"
    assert cfg.continue_processing is True
    assert cfg.verbose is True

