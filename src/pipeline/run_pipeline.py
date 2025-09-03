from __future__ import annotations

import os
import re
import shutil
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

# Ensure project root on sys.path so we can import existing modules at repo root
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline.config import PipelineConfig
from src.pipeline.healthchecks import check_ollama
from src.pipeline.logging import get_logger
from src.pipeline.manifest import RunManifest, compute_run_id, sha256_file, sha256_text
from src.pipeline.metrics import Metrics

# Import from existing code (do not modify those files)
from book2text import main as extract_main
from sum import process_csv_input, Config as SummarizeConfig


def sanitize_model_for_filename(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


def run_pipeline(input_file: str, cfg: PipelineConfig) -> Dict[str, Any]:
    logger = get_logger("pipeline")

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if input_path.suffix.lower() not in {".pdf", ".epub"}:
        raise ValueError("Only .pdf and .epub inputs are supported")

    # Healthcheck Ollama
    ok, msg = check_ollama(cfg.api_base, cfg.model)
    logger.info(msg)
    if not ok:
        raise RuntimeError(msg)

    # Prepare run directory
    book_name = re.sub(r"[^\w\-]+", "-", input_path.stem)
    input_hash = sha256_file(input_path)
    run_id = compute_run_id(book_name, input_hash, cfg.model, cfg.prompt_alias)
    run_root = Path(cfg.output_root) / book_name / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    metrics = Metrics(run_root)

    # Manifest skeleton
    pipeline_cfg_hash = sha256_text(
        f"env={cfg.env}|api_base={cfg.api_base}|model={cfg.model}|prompt={cfg.prompt_alias}|output={cfg.output_root}"
    )
    manifest = RunManifest(
        run_id=run_id,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        env=cfg.env,
        input_file=str(input_path.resolve()),
        input_sha256=input_hash,
        input_bytes=input_path.stat().st_size,
        pipeline_config_hash=pipeline_cfg_hash,
        model=cfg.model,
        prompt_alias=cfg.prompt_alias,
        api_base=cfg.api_base,
    )

    # Step 1: Extract + chunk to CSV
    t0 = time.perf_counter()
    output_dir = run_root / "split"
    raw_csv = run_root / f"{book_name}.csv"
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics.record("extract:start", {"output_dir": str(output_dir), "csv": str(raw_csv)})
    logger.info("Starting extract", extra={"step": "extract", "csv": str(raw_csv)})
    extract_main(str(input_path), str(output_dir), str(raw_csv))
    t1 = time.perf_counter()
    metrics.record("extract:end", {"duration_s": round(t1 - t0, 3)})

    # book2text also writes a processed CSV via lib/chunking into CWD. Move it into run dir if present.
    processed_csv_cwd = Path.cwd() / f"{book_name}_processed.csv"
    processed_csv_run = run_root / f"{book_name}_processed.csv"
    if processed_csv_cwd.exists():
        try:
            shutil.move(str(processed_csv_cwd), str(processed_csv_run))
            manifest.artifacts["processed_csv"] = str(processed_csv_run)
        except Exception:
            # leave it in place if move fails
            manifest.artifacts["processed_csv"] = str(processed_csv_cwd)

    manifest.artifacts["split_dir"] = str(output_dir)
    manifest.artifacts["raw_csv"] = str(raw_csv)

    # Step 2: Summarize via Ollama
    t2 = time.perf_counter()
    s_cfg = SummarizeConfig()  # uses _config.yaml for prompts
    model = cfg.model
    model_safe = sanitize_model_for_filename(model)
    markdown_file = run_root / f"{book_name}_{model_safe}.md"
    csv_file = run_root / f"{book_name}_{model_safe}.csv"

    metrics.record("summarize:start", {"model": model, "prompt": cfg.prompt_alias})
    logger.info("Starting summarize", extra={"step": "summarize", "model": model, "prompt": cfg.prompt_alias})

    process_csv_input(
        input_file=str(raw_csv),
        config=s_cfg,
        api_base=cfg.api_base,
        model=model,
        prompt_alias=cfg.prompt_alias,
        ptitle=s_cfg.title_prompt,
        markdown_file=str(markdown_file),
        csv_file=str(csv_file),
        verbose=cfg.verbose,
        continue_processing=cfg.continue_processing,
    )

    t3 = time.perf_counter()
    metrics.record("summarize:end", {"duration_s": round(t3 - t2, 3)})

    manifest.artifacts["summary_markdown"] = str(markdown_file)
    manifest.artifacts["summary_csv"] = str(csv_file)

    # Finalize manifest
    manifest.write(run_root / "run_manifest.json")
    metrics.record("pipeline:done", {"total_duration_s": round(t3 - t0, 3)})
    logger.info("Pipeline done", extra={"run_dir": str(run_root)})

    return {
        "run_dir": str(run_root),
        "manifest": asdict(manifest),
    }

