FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared backend code (agents, skills, models, db)
COPY backend/ /app/backend/

# Copy worker code
COPY worker/ /app/worker/

EXPOSE ${PORT:-8080}

# Run worker
CMD ["python", "-m", "worker.main"]
