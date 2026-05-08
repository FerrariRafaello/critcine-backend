# _ Stage 1: builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/packages

# _ Stage 2: Production
FROM python:3.12-slim
WORKDIR /app

# _ Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /app/packages /app/packages
COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

ENV PYTHONPATH=/app/packages

# _ Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]