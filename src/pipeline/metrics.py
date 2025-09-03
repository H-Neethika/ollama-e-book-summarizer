from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass
class MetricEvent:
    event: str
    data: Dict[str, Any]


class Metrics:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.file = self.output_dir / "metrics.jsonl"

    def record(self, event: str, data: Dict[str, Any] | None = None) -> None:
        payload = MetricEvent(event=event, data=data or {})
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": payload.event,
            "data": payload.data,
        }
        with self.file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

