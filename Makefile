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