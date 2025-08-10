# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (ensure SQLite tooling exists)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install requirements first (better cache)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY app ./app
COPY instructions.txt ./instructions.txt

EXPOSE 8000 8501

# Default command: run FastAPI
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


