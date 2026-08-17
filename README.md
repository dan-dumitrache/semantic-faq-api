# Semantic FAQ API

A production-oriented FastAPI service that retrieves answers from a semantic
FAQ knowledge base and uses a guarded OpenAI fallback when no confident local
match exists.

## Features

- OpenAI embeddings through LangChain
- PostgreSQL and pgvector semantic search
- Incremental, content-hash-based embedding synchronization
- Configurable confidence and ambiguity routing
- Out-of-domain compliance routing
- Prompt-injection input guards
- Bearer-token authentication using FastAPI dependencies
- Deterministic unit and API tests
- Docker Compose environment
- Ruff, mypy, pytest, and GitHub Actions

## Request flow

1. Authenticate the caller.
2. Validate and normalize the question.
3. Reject recognized prompt-injection patterns.
4. Route clearly unrelated questions to a fixed compliance response.
5. Embed supported questions.
6. retrieve the two most similar FAQ records.
7. Assess similarity and ambiguity.
8. Return a local answer for a confident match.
9. Otherwise, use the guarded OpenAI fallback.

## Local setup

Requirements:

- Python 3.12
- Docker
- OpenAI API key