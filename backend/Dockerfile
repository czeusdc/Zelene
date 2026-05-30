FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for asyncpg and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy everything first (pyproject.toml + source code)
COPY . .

# Install the package so `from src.xxx` imports work
RUN pip install --no-cache-dir ".[dev]"

# Cloud Run sets PORT env variable (default 8080)
ENV PORT=8080

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
