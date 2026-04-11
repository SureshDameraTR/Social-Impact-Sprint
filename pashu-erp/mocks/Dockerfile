FROM python:3.12-slim
RUN adduser --disabled-password --no-create-home --gecos "" appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p uploads && chown appuser:appuser uploads
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
