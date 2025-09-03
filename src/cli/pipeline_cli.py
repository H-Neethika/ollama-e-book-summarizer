from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.pipeline.config import load_config, PipelineConfig
from src.pipeline.run_pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run the e-book summarization pipeline end-to-end",
    )
    p.add_argument("input_file", help="Path to input .pdf or .epub")
    p.add_argument("--env", default=None, help="Environment name (maps to configs/config.<env>.yaml)")
    p.add_argument("--config", default=None, help="Explicit config path (overrides --env)")
    p.add_argument("--api-base", dest="api_base", default=None, help="Override Ollama API base URL")
    p.add_argument("--model", default=None, help="Override model (e.g., gemma:2b)")
    p.add_argument("--prompt", dest="prompt_alias", default=None, help="Override prompt alias (e.g., bnotes)")
    p.add_argument("--output-root", dest="output_root", default=None, help="Where to write runs/ (default from config)")
    p.add_argument("--continue", dest="cont", action="store_true", help="Continue from last processed row if supported")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose summarize output")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(env=args.env, config_path=args.config)

    # CLI overrides
    if args.api_base:
        cfg.api_base = args.api_base
    if args.model:
        cfg.model = args.model
    if args.prompt_alias:
        cfg.prompt_alias = args.prompt_alias
    if args.output_root:
        cfg.output_root = args.output_root
    if args.cont:
        cfg.continue_processing = True
    if args.verbose:
        cfg.verbose = True

    result = run_pipeline(args.input_file, cfg)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

