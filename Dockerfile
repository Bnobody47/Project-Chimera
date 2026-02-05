# Project Chimera — containerized dev/test environment
# Spec-driven autonomous influencer agent swarm
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY skills/ skills/
COPY tests/ tests/
COPY Makefile ./

ENV PYTHONPATH=/app

RUN pip install --no-cache-dir pytest pydantic

CMD ["make", "test"]
