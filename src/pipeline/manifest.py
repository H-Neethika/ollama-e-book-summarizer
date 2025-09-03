from __future__ import annotations

import json
import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return _sha256_bytes(text.encode("utf-8"))


@dataclass
class RunManifest:
    run_id: str
    created_at: str
    env: str
    input_file: str
    input_sha256: str
    input_bytes: int
    pipeline_config_hash: str
    model: str
    prompt_alias: str
    api_base: str
    git_commit: str = ""
    artifacts: Dict[str, str] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def write(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("w", encoding="utf-8") as fh:
            fh.write(self.to_json())


def compute_run_id(book_name: str, input_hash: str, model: str, prompt_alias: str) -> str:
    seed = f"{book_name}|{input_hash[:12]}|{model}|{prompt_alias}"
    digest = sha256_text(seed)[:12]
    return f"{book_name}-{digest}"
