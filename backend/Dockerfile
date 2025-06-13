FROM python:3.11-slim

# --- Install system dependencies including Tesseract OCR ---
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# --- Setup app directory ---
WORKDIR /app
ENV TRANSFORMERS_CACHE=/app/cache
RUN mkdir -p /app/cache && chmod -R 777 /app/cache
# --- Install Python dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy source code ---
COPY . .

# --- Expose app port ---
EXPOSE 8000

# --- Start server ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
