# Multi-stage build for nanobot gateway

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY --from=workspace pyproject.toml uv.lock /app/
COPY pyproject.toml /app/nanobot/pyproject.toml
COPY --from=mcp . /app/mcp
COPY --from=nanobot-websocket-channel . /app/nanobot-websocket-channel
COPY . /app/nanobot

RUN --mount=type=cache,target=/root/.cache/uv \
    cd /app/nanobot && uv sync --frozen

# ---
ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

WORKDIR /app/nanobot

# Copy from builder as root
COPY --from=builder /app /app

# Store the venv in a location that won't be hidden by volume mounts
RUN mv /app/nanobot/.venv /opt/nanobot-venv

ENV PATH="/opt/nanobot-venv/bin:$PATH"

CMD ["python", "/app/nanobot/entrypoint.py"]
