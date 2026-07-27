# syntax=docker/dockerfile:1

# --- Stage 1: resolve and install dependencies with uv -----------------------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install locked dependencies only (layer is cached until pyproject/uv.lock change)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

# --- Stage 2: runtime image (no uv, no build tools) ---------------------------
FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="picking-route" \
      org.opencontainers.image.description="Warehouse order batching & picking-route optimisation Streamlit app" \
      org.opencontainers.image.source="https://github.com/samirsaci/picking-route" \
      org.opencontainers.image.licenses="MIT"

# Run as an unprivileged user
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY app.py ./
COPY utils/ ./utils/
COPY static/ ./static/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# The app saves generated charts under static/out at runtime
RUN mkdir -p static/out && chown -R app:app /app/static/out

USER app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
