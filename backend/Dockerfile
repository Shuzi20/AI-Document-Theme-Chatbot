# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OCR (Tesseract)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (leverage Docker cache)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY . .

# Expose Hugging Face Spaces default port
EXPOSE 7860

# Command to run FastAPI app using Uvicorn on Hugging Face expected port
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
