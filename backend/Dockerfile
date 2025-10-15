########################################
# Multi-stage build for FastAPI backend #
########################################

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN apt-get update && apt-get install -y gcc g++ make libffi-dev postgresql-client && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Install postgresql-client for database wait
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
# Security: create non-root user
RUN useradd -m sparta && mkdir -p /app && chown sparta:sparta /app
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir --find-links=/wheels -r requirements.txt
USER sparta
COPY --chown=sparta:sparta app/ ./app
COPY --chown=sparta:sparta init_db.py ./init_db.py
COPY --chown=sparta:sparta groq_examples.py ./groq_examples.py
COPY --chown=sparta:sparta entrypoint.sh ./entrypoint.sh
USER root
RUN chmod +x entrypoint.sh && chown sparta:sparta entrypoint.sh
ENV PATH="/home/sparta/.local/bin:${PATH}"
USER sparta
# Set environment variables for Docker networking
ENV DATABASE_URL=postgresql+psycopg://sparta:sparta_pass@db:5432/sparta_db
ENV REDIS_URL=redis://redis:6379/0
# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
# Expose port
EXPOSE 8000
# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
