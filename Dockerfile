FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Volumes mounted here inherit this ownership on first use.
RUN useradd --system --uid 1000 app \
    && mkdir -p /data /app/staticfiles \
    && chown app /data /app/staticfiles
USER app

EXPOSE 8000
# One worker: the checkout rate limiter lives in per-process memory.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && exec gunicorn eshop.wsgi --bind 0.0.0.0:8000 --workers 1 --threads 4 --no-control-socket --access-logfile -"]
