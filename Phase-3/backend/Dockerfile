

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (build essentials for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies via uv lockfile export
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv export --format requirements-txt --no-dev --output-file requirements.txt \
    && pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

# Copy application code
COPY app ./app
COPY main.py ./main.py
COPY create_auth_tables.py ./create_auth_tables.py

EXPOSE 8001

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
