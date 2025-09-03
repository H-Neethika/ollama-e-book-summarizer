from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        # Include any extra dict if present
        for k, v in record.__dict__.items():
            if k not in ("name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module",
                         "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs",
                         "relativeCreated", "thread", "threadName", "processName", "process"):
                base[k] = v
        return json.dumps(base, ensure_ascii=False)


def get_logger(name: str, level: str | int | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level_name = level or os.getenv("LOG_LEVEL", "INFO")
    lvl = getattr(logging, str(level_name).upper(), logging.INFO)
    logger.setLevel(lvl)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger

