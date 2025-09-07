FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/data/hf \
    TRANSFORMERS_CACHE=/data/transformers

WORKDIR /app

# System packages: wkhtmltopdf for PDF export, fonts, git (optional)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       wkhtmltopdf \
       fonts-dejavu-core \
       libglib2.0-0 libxrender1 libfontconfig1 libxext6 \
       git \
    && rm -rf /var/lib/apt/lists/*

# Create caches for HF/transformers
RUN mkdir -p /data/hf /data/transformers

COPY requirements.txt ./

# Install CPU-only torch first to avoid pulling CUDA wheels, then the rest
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.4.1 \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8501

# Default to Streamlit app; can be overridden
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
