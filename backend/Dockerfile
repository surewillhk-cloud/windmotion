FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/backend/
CMD ["sh", "-c", "python -m backend.db.migrations.run_migrations 2>&1 || echo 'Migration skipped'; exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
