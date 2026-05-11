FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Build context is repo root (Railway Root Directory=/)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

EXPOSE ${PORT:-8080}

# Run migrations (non-fatal) then start server
CMD ["sh", "-c", "python -m backend.db.migrations.run_migrations 2>&1 || echo 'Migration skipped'; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
