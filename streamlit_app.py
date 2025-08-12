import streamlit as st
import os
from book2text import main as extract_main
from sum import process_csv_input, Config

st.title("📚 Ebook Summarizer")
uploaded_file = st.file_uploader("Upload your PDF or EPUB", type=["pdf", "epub"])

if uploaded_file:
    filename = uploaded_file.name
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded: {filename}")
    st.write("🔄 Starting summarization...")

    # Set file paths
    file_name_no_ext = os.path.splitext(filename)[0]
    output_dir = os.path.join("out", file_name_no_ext)
    output_csv = os.path.join("out", f"{file_name_no_ext}.csv")

    # Step 1: Extract and process file
    extract_main(filename, output_dir, output_csv)

    # Step 2: Summarize
    config = Config()
    model = "gemma:2b"
    prompt_alias = config.defaults.get("prompt", "DEFAULT_PROMPT_ALIAS")
   # Sanitize model name for use in file names
    model_safe = model.replace("/", "_").replace(":", "_")

    markdown_file = f"{file_name_no_ext}_{model_safe}.md"
    csv_file = f"{file_name_no_ext}_{model_safe}.csv"


    process_csv_input(
        input_file=output_csv,
        config=config,
        api_base="http://localhost:11434/api",
        model=model,
        prompt_alias=prompt_alias,
        ptitle=config.title_prompt,
        markdown_file=markdown_file,
        csv_file=csv_file,
        verbose=False,
        continue_processing=False
    )


    st.success("🎉 Summarization Complete!")

    # Load and display the Markdown output
    if os.path.exists(markdown_file):
        with open(markdown_file, "r", encoding="utf-8") as md:
            st.markdown(md.read(), unsafe_allow_html=True)
