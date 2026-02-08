FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements.txt .

COPY ./requirements.txt ./temp_requirements.txt

RUN grep -v "^ai-mcp" temp_requirements.txt > ./root_requirements.txt || echo "# No ai-mcp in requirements" > /dev/null

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim AS runner

WORKDIR /app

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=appuser:appgroup /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder --chown=appuser:appgroup /usr/local/bin /usr/local/bin

COPY --chown=appuser:appgroup ./backend/ .

COPY --chown=appuser:appgroup ./src ./src

# Switch to non-root user
USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/docs || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]