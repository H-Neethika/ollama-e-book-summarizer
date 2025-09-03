from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import yaml


@dataclass
class PipelineConfig:
    env: str = "dev"
    api_base: str = "http://localhost:11434/api"
    model: str = "gemma:2b"
    prompt_alias: str = "bnotes"
    output_root: str = "runs"
    continue_processing: bool = False
    verbose: bool = False

    # Optional fields for future use
    extras: Optional[Dict[str, Any]] = None


def _from_yaml(cfg: Dict[str, Any]) -> PipelineConfig:
    p = PipelineConfig()
    if not cfg:
        return p
    p.env = cfg.get("env", p.env)
    p.api_base = cfg.get("api_base", p.api_base)
    p.model = cfg.get("model", p.model)
    p.prompt_alias = cfg.get("prompt_alias", p.prompt_alias)
    p.output_root = cfg.get("output_root", p.output_root)
    p.continue_processing = bool(cfg.get("continue_processing", p.continue_processing))
    p.verbose = bool(cfg.get("verbose", p.verbose))
    p.extras = cfg.get("extras", {}) or {}
    return p


def load_config(env: Optional[str] = None, config_path: Optional[str | Path] = None) -> PipelineConfig:
    """Load pipeline configuration from a yaml file and environment variables.

    Order of precedence (lowest → highest):
    - defaults in code
    - YAML file (configs/config.<env>.yaml or explicit path)
    - environment variables (EBOOKSUM_*)
    """

    # Base from defaults
    cfg = PipelineConfig()

    # Determine env and config path
    env_name = env or os.getenv("EBOOKSUM_ENV", cfg.env)
    if config_path:
        cfg_path = Path(config_path)
    else:
        cfg_path = Path("configs") / f"config.{env_name}.yaml"

    if cfg_path.exists():
        with cfg_path.open("r", encoding="utf-8") as fh:
            yaml_cfg = yaml.safe_load(fh) or {}
        cfg = _from_yaml(yaml_cfg)
    else:
        # keep defaults if file missing; this is fine for local dev
        cfg.env = env_name

    # Env var overrides
    cfg.api_base = os.getenv("EBOOKSUM_API_BASE", cfg.api_base)
    cfg.model = os.getenv("EBOOKSUM_MODEL", cfg.model)
    cfg.prompt_alias = os.getenv("EBOOKSUM_PROMPT", cfg.prompt_alias)
    cfg.output_root = os.getenv("EBOOKSUM_OUTPUT_ROOT", cfg.output_root)

    # Booleans
    cont = os.getenv("EBOOKSUM_CONTINUE")
    if cont is not None:
        cfg.continue_processing = cont.lower() in {"1", "true", "yes", "y"}

    verb = os.getenv("EBOOKSUM_VERBOSE")
    if verb is not None:
        cfg.verbose = verb.lower() in {"1", "true", "yes", "y"}

    return cfg

