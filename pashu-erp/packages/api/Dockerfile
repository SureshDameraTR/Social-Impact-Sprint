FROM python:3.12-slim AS builder

LABEL maintainer="PashuRaksha Team"
LABEL org.opencontainers.image.source="https://github.com/pashuraksha/erp"
LABEL org.opencontainers.image.description="PashuRaksha ERP API"

WORKDIR /app

RUN pip install uv==0.6.0

COPY pyproject.toml .
RUN uv pip install --system -e .

COPY . .

# --- Runtime stage ---
FROM python:3.12-slim

LABEL maintainer="PashuRaksha Team"
LABEL org.opencontainers.image.source="https://github.com/pashuraksha/erp"
LABEL org.opencontainers.image.description="PashuRaksha ERP API"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' --uid 1001 appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD ["curl", "-f", "http://localhost:8000/health"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
