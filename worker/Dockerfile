FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared backend code
COPY backend/ /app/backend/

# Copy worker code
COPY worker/ /app/worker/

# Default: run worker
CMD ["python", "-m", "worker.main"]
