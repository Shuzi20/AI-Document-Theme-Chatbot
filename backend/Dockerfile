FROM python:3.11-slim

# --- Install system dependencies including build tools and OCR ---
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# --- Setup app directory ---
WORKDIR /app

# ✅ Set Hugging Face cache environment for model/tokenizer downloads
ENV TRANSFORMERS_CACHE=/app/.hf_cache
ENV HF_HOME=/app/.hf_cache

# ✅ Create writable cache directory
RUN mkdir -p /app/.hf_cache && chmod -R 777 /app/.hf_cache

# --- Install Python dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application code ---
COPY . .

# --- Expose app port ---
EXPOSE 8000

# --- Start FastAPI server ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
