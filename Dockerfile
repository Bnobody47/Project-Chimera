# Project Chimera — Multi-stage containerized environment
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml requirements.txt requirements-dev.txt ./

# Install dependencies into virtual environment
RUN uv pip install --system -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY pyproject.toml ./
COPY skills/ skills/
COPY tests/ tests/
COPY Makefile ./
COPY .dockerignore ./

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check for services (when implemented)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Default: run tests
CMD ["make", "test"]
