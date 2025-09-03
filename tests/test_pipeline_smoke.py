from __future__ import annotations

from pathlib import Path

from scripts.gen_sample_pdf import main as gen_pdf


def test_pipeline_smoke(monkeypatch, tmp_path):
    # Import here to allow monkeypatching names inside the module
    from src.pipeline import run_pipeline as rp
    from src.pipeline.config import PipelineConfig

    # Prepare sample PDF
    sample_pdf = tmp_path / "sample.pdf"
    gen_pdf(str(sample_pdf))

    # Stub healthcheck and heavy functions
    monkeypatch.setattr(rp, "check_ollama", lambda *a, **k: (True, "ok"))

    def fake_extract_main(in_file: str, out_dir: str, out_csv: str):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        # Write a minimal CSV with headers expected by sum.process_csv_input
        Path(out_csv).write_text("title,text\nIntro,This is a test.\n", encoding="utf-8")

    def fake_process_csv_input(**kwargs):
        # Write outputs referenced by pipeline
        Path(kwargs["markdown_file"]).write_text("# Test\nBody\n", encoding="utf-8")
        Path(kwargs["csv_file"]).write_text("Title,Was_Generated,Text,model_name,Time,Len\n", encoding="utf-8")

    monkeypatch.setattr(rp, "extract_main", fake_extract_main)
    monkeypatch.setattr(rp, "process_csv_input", fake_process_csv_input)

    cfg = PipelineConfig(env="dev", output_root=str(tmp_path / "runs"))
    result = rp.run_pipeline(str(sample_pdf), cfg)
    run_dir = Path(result["run_dir"]) 
    assert run_dir.exists()
    md = Path(result["manifest"]["artifacts"]["summary_markdown"]) 
    assert md.exists()

