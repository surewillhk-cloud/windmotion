# ── All-in-one: Backend + Worker + Frontend ──
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl nginx nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY backend/ /app/backend/
COPY worker/ /app/worker/
COPY frontend/ /app/frontend/

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build
WORKDIR /app

# Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE ${PORT:-8080}

CMD ["/app/start.sh"]
