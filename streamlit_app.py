import os
from pathlib import Path

import streamlit as st

from src.pipeline.config import load_config
from src.pipeline.run_pipeline import run_pipeline

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from textwrap import wrap
from io import BytesIO
import pdfkit
import markdown2
import yaml
import shutil
import platform

project_root = Path(__file__).parent
wkhtmltopdf_path = project_root / "wkhtmltopdf.exe"

def markdown_to_pdf(text: str) -> BytesIO:
    html_content = markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
    html_template = f"""
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3, h4 {{ color: #222; }}
        ul {{ margin-left: 20px; }}
        li {{ margin-bottom: 5px; }}
        p {{ line-height: 1.5; }}
      </style>
    </head>
    <body>
      {html_content}
    </body>
    </html>
    """

    # Use bundled .exe only on Windows; otherwise auto-detect in PATH
    is_windows = platform.system().lower().startswith("win")
    wk_bin = None
    if is_windows and wkhtmltopdf_path.exists():
        wk_bin = str(wkhtmltopdf_path)
    else:
        wk_bin = shutil.which("wkhtmltopdf")
    if wk_bin:
        config = pdfkit.configuration(wkhtmltopdf=wk_bin)
        pdf_bytes = pdfkit.from_string(html_template, False, configuration=config)
    else:
        # Let pdfkit try default, or raise a clear error if missing
        try:
            pdf_bytes = pdfkit.from_string(html_template, False)
        except OSError as e:
            raise FileNotFoundError(
                "wkhtmltopdf not found. Install it (e.g., 'sudo apt-get install wkhtmltopdf' on Linux, 'brew install wkhtmltopdf' on macOS)"
            ) from e
    return BytesIO(pdf_bytes)


st.title("📚 Ebook Summarizer")

with st.sidebar:
    st.header("Settings")
    env = st.text_input("Environment", value=os.getenv("EBOOKSUM_ENV", "dev"))
    api_base = st.text_input("Ollama API Base", value=os.getenv("EBOOKSUM_API_BASE", "http://localhost:11434/api"))
    model = st.text_input("Model", value=os.getenv("EBOOKSUM_MODEL", "gemma:2b"))
    prompt_alias = st.text_input("Prompt Alias", value=os.getenv("EBOOKSUM_PROMPT", "bnotes"))
    cont = st.checkbox("Continue from last processed", value=False)
    verbose = st.checkbox("Verbose output", value=False)

    st.divider()
    backend = st.selectbox("Summarization Backend", options=["ollama", "transformers"], index=0)
    # Transformers backend settings
    t_base_model = st.text_input("Base model (HF repo or path)", value="google/gemma-2b") if backend == "transformers" else None
    t_lora_path = st.text_input("LoRA path (local folder)", value="./gemma2b-cnn-lora") if backend == "transformers" else None
    t_device = st.selectbox("Device", options=["auto", "cpu", "cuda"], index=0) if backend == "transformers" else None
    t_dtype = st.selectbox("Dtype", options=["auto", "float16", "bfloat16", "float32"], index=0) if backend == "transformers" else None
    t_max_new_tokens = st.number_input("Max new tokens", min_value=32, max_value=4096, value=512, step=32) if backend == "transformers" else None
    t_temperature = st.slider("Temperature", min_value=0.0, max_value=1.5, value=0.5, step=0.05) if backend == "transformers" else None
    t_top_p = st.slider("Top-p", min_value=0.1, max_value=1.0, value=0.95, step=0.05) if backend == "transformers" else None
    t_rep = st.slider("Repetition penalty", min_value=0.8, max_value=2.0, value=1.1, step=0.05) if backend == "transformers" else None

uploaded_file = st.file_uploader("Upload your PDF or EPUB", type=["pdf", "epub"])

if uploaded_file:
    filename = uploaded_file.name
    tmp_path = Path(".streamlit_uploads")
    tmp_path.mkdir(parents=True, exist_ok=True)
    local_path = tmp_path / filename
    with local_path.open("wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded: {filename}")
    st.write("🔄 Running pipeline...")

    cfg = load_config(env=env)
    cfg.api_base = api_base or cfg.api_base
    cfg.model = model or cfg.model
    cfg.prompt_alias = prompt_alias or cfg.prompt_alias
    cfg.continue_processing = cont
    cfg.verbose = verbose

    # Update root _config.yaml to reflect backend choice (used by sum.py)
    try:
        root_cfg_path = Path(__file__).parent / "_config.yaml"
        if root_cfg_path.exists():
            with root_cfg_path.open("r", encoding="utf-8") as fh:
                root_cfg = yaml.safe_load(fh) or {}
        else:
            root_cfg = {}

        root_cfg["backend"] = backend
        if backend == "transformers":
            root_cfg.setdefault("transformers", {})
            root_cfg["transformers"].update({
                "base_model": t_base_model or "google/gemma-2b",
                "lora_path": t_lora_path or "./gemma2b-cnn-lora",
                "max_new_tokens": int(t_max_new_tokens or 512),
                "temperature": float(t_temperature or 0.5),
                "top_p": float(t_top_p or 0.95),
                "repetition_penalty": float(t_rep or 1.1),
                "dtype": t_dtype or "auto",
                "device": t_device or "auto",
            })

        with root_cfg_path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(root_cfg, fh, sort_keys=False, allow_unicode=True)

    except Exception as e:
        st.warning(f"Failed to update _config.yaml for backend selection: {e}")

    try:
        result = run_pipeline(str(local_path), cfg)
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
    else:
        st.success("🎉 Summarization Complete!")
        manifest = result.get("manifest", {})
        md_path = manifest.get("artifacts", {}).get("summary_markdown")


        if md_path and Path(md_path).exists():
            with open(md_path, "r", encoding="utf-8") as md:
                summary_text = md.read()
                st.markdown(summary_text, unsafe_allow_html=True)

                # Generate styled PDF
                pdf_buffer = markdown_to_pdf(summary_text)

                st.download_button(
                    label="⬇️ Export Summary",
                    data=pdf_buffer,
                    file_name="summary.pdf",
                    mime="application/pdf"
                )


        else:
            st.info("Markdown summary not found in artifacts.")
