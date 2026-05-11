FROM python:3.11-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install Python deps (paths relative to build context = repo root)
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source
COPY backend/ /app/backend/
COPY worker/ /app/worker/

# Default port (Railway sets $PORT)
ENV PORT=8080
EXPOSE $PORT

CMD ["sh", "-c", "python -m backend.db.migrations.run_migrations 2>&1 || echo 'Migration skipped'; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
