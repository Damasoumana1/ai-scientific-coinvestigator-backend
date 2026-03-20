FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --default-timeout=100 --retries 10 -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploaded_files

# Create non-root user with UID 1000 for Hugging Face compatibility
RUN useradd -m -u 1000 user \
    && chown -R user /app

# Set environment variables for HF
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

USER user

# Expose port (7860 for Hugging Face)
EXPOSE 7860

# Health check (adapted for 7860)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health/ || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
