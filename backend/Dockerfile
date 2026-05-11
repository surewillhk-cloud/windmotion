FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Railway rootDirectory=/backend, so build context IS the backend/ directory.
# requirements.txt is at the root of the build context.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from build context (backend/) into /app/backend/
COPY . /app/backend/

EXPOSE ${PORT:-8000}

# Run migrations (non-fatal) then start server
CMD ["sh", "-c", "python -m backend.db.migrations.run_migrations 2>&1 || echo 'Migration skipped'; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
