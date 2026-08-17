FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --prefix=/install .


FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/app/bin:${PATH}"

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /opt/app

COPY --from=builder /install /usr/local
COPY scripts ./scripts
COPY data ./data

USER app

EXPOSE 8000

CMD ["uvicorn", "semantic_faq.main:app", "--host", "0.0.0.0", "--port", "8000"]

'docker-compose.yml'

yaml

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: faq
      POSTGRES_USER: faq
      POSTGRES_PASSWORD: faq
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faq -d faq"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  embedding-sync:
    build: .
    command: ["python", "scripts/sync_embeddings.py"]
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://faq:faq@postgres:5432/faq
    depends_on:
      postgres:
        condition: service_healthy
    restart: "no"

  api:
    build: .
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://faq:faq@postgres:5432/faq
    depends_on:
      postgres:
        condition: service_healthy
      embedding-sync:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
    restart: unless-stopped

volumes:
  postgres_data:

'Makefile'

"Makefile command interactions must use tabs"

makefile

.PHONY: install check test run up down sync

install:
	python -m pip install -e ".[dev]"

check:
	ruff format --check .
	ruff check .
	mypy src

test:
	pytest --cov=semantic_faq --cov-report=term-missing

run:
	uvicorn semantic_faq.main:app --reload

up:
	docker compose up --build

down:
	docker compose down

sync:
	python scripts/sync_embeddings.py
