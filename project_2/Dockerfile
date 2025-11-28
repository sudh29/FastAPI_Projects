# =========================
# Stage 1 — Builder
# =========================
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (temporary)
RUN apk add --no-cache --virtual .build-deps \
    build-base linux-headers libffi-dev

# Copy requirements and install into a temporary directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# =========================
# Stage 2 — Runtime
# =========================
FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Only install runtime system dependencies
RUN apk add --no-cache tini

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY . .

# Expose port
EXPOSE ${PORT}

# Use Tini for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Run uvicorn server for FastAPI
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
