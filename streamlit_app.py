import os
from pathlib import Path

import streamlit as st

from src.pipeline.config import load_config
from src.pipeline.run_pipeline import run_pipeline


st.title("📚 Ebook Summarizer")

with st.sidebar:
    st.header("Settings")
    env = st.text_input("Environment", value=os.getenv("EBOOKSUM_ENV", "dev"))
    api_base = st.text_input("Ollama API Base", value=os.getenv("EBOOKSUM_API_BASE", "http://localhost:11434/api"))
    model = st.text_input("Model", value=os.getenv("EBOOKSUM_MODEL", "gemma:2b"))
    prompt_alias = st.text_input("Prompt Alias", value=os.getenv("EBOOKSUM_PROMPT", "bnotes"))
    cont = st.checkbox("Continue from last processed", value=False)
    verbose = st.checkbox("Verbose output", value=False)

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
                st.markdown(md.read(), unsafe_allow_html=True)
        else:
            st.info("Markdown summary not found in artifacts.")
