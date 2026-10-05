FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies required for building psycopg2 and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

EXPOSE 8000

# Default command starts pre_start (DB wait + migrations + seed) and uvicorn
CMD ["sh", "-c", "python -m src.pre_start && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
