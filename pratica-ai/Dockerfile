# === FILE: Dockerfile ===
# Multi-stage production Dockerfile for Sinistri FNOL Agent
# Italian insurance claim voice agent — GDPR compliant

# ── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

# Install system-wide (no --user) so packages land in /usr/local
# and are accessible to any user including appuser
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir asyncpg psycopg2-binary redis

# ── Stage 2: Production ─────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy system-wide site-packages and scripts from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY . .

RUN chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 4177

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:4177/health || exit 1

USER appuser

CMD ["uvicorn", "live_demo.server:app", "--host", "0.0.0.0", "--port", "4177", "--workers", "2"]
