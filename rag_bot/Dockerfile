FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QF_DATA_DIR=/app/data \
    QF_INDEX_DIR=/app/indexes/default \
    QF_LOG_DIR=/app/logs \
    QF_EMBEDDING_BACKEND=hashing

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY data ./data
COPY README.md ./README.md

EXPOSE 8000

CMD ["sh", "-c", "python scripts/build_index.py && uvicorn app.api:app --host 0.0.0.0 --port 8000"]

