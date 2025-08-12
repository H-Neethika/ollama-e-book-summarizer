# 📚 E-Book Summarizer (Lightweight LLM Version)

A local, privacy-friendly tool to summarize books and research PDFs using the lightweight `gemma:2b` model via [Ollama](https://ollama.com). Everything runs in your browser via a simple Streamlit UI — **no cloud APIs or GPU required**.

---

## ✨ Features

- ✅ Accepts EPUB and PDF files
- 🔁 Automatically chunks chapters (~2000 tokens each)
- 📝 Summarizes each chunk with `gemma:2b`
- 🧠 Title generation for each section
- 🧾 Exports summaries as CSV and Markdown
- ⚙️ Runs entirely offline using Ollama and CPU

---

## 🛠 Setup

### 1. Clone the repository & create a virtual environment

```bash
git clone https://github.com/your-username/ollama-ebook-summary
cd ollama-ebook-summary
python -m venv venv
venv\Scripts\activate  # for Windows
# OR
source venv/bin/activate  # for Mac/Linux
```

---

### 2. Install required Python packages

```bash
pip install -r requirements.txt
```

---

### 3. Install Ollama & pull the small LLM

- Download and install Ollama: https://ollama.com/download
- Pull the Gemma 2B model:

```bash
ollama pull gemma:2b
```

---


---

## 🚀 How to Run

```bash
streamlit run streamlit_app.py
```

Once running, open in your browser at:  
📍 [http://localhost:8501](http://localhost:8501)

---

## 📂 Output

After processing, your output will be saved in:

- `out/{book-id}/...` – split PDFs by chapter
- `out/{book-id}.csv` – raw section metadata
- `{book-id}_gemma:2b.csv` – final summary results
- `{book-id}_gemma:2b.md` – formatted markdown summary

---

## 🧠 About Chunking

Each chapter/section is chunked into ~2000 token blocks based on:
- Table of Contents (for EPUBs and tagged PDFs)
- Manual fallback if ToC metadata is missing

Why 2000 tokens?  
👉 Research shows LLM reasoning stabilizes around 2000-3000 tokens ([source](https://huggingface.co/papers/2402.14848)).

---

## 📌 Notes

- You only need to run `streamlit_app.py` — no manual CLI steps!
- `gemma:2b` is small and runs on CPU — perfect for laptops or low-end PCs.
- You can later upgrade to heavier models if you want better quality.

---

## ✅ Requirements

- Python 3.11+
- Ollama installed and running in the background
- At least 4 GB free RAM recommended

---

## 🧠 Credits & Acknowledgements

- Model: [Gemma 2B](https://ollama.com/library/gemma) via Ollama
- Inspired by open-source research summarization workflows


