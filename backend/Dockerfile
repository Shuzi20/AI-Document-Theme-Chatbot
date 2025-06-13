FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 libxrender1 libxext6 \
    build-essential g++ python3-dev libc-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV TRANSFORMERS_CACHE=/app/.hf_cache HF_HOME=/app/.hf_cache
RUN mkdir -p /app/.hf_cache && chmod -R 777 /app/.hf_cache

COPY requirements.txt .
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
