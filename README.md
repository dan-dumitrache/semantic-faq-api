## Semantic FAQ Routing Service — Technical Challenge Submission

```text
Production-oriented FastAPI service for semantic FAQ retrieval with pgvector, confidence-based routing, guarded OpenAI fallback, deterministic tests, Docker, and CI.


This repository contains a production-oriented question-answering API that uses semantic search to retrieve answers from a local FAQ knowledge base and falls back to an OpenAI model when no sufficiently reliable local match is available.

The solution is implemented in Python with FastAPI, LangChain, PostgreSQL, and pgvector. Its design emphasizes maintainability, testability, security, deterministic behavior, and a clear path toward production scaling.

### Core behavior

For each incoming question, the service:

1. Authenticates the request using bearer-token authentication.
2. Validates and normalizes the input.
3. Applies security checks for common prompt-injection and jailbreak patterns.
4. Routes clearly unsupported questions to a deterministic compliance response.
5. Generates an embedding for supported questions.
6. Searches the local FAQ knowledge base using cosine similarity.
7. Evaluates the best candidates using:
   - A configurable minimum similarity threshold.
   - An ambiguity margin between the two best results.
8. Returns the stored FAQ answer when the match is sufficiently confident.
9. Uses a guarded OpenAI fallback when the local result is missing, weak, or ambiguous.

A successful response identifies whether the answer came from the local knowledge base, the OpenAI fallback, or the compliance route.

### Architecture

The application follows a ports-and-adapters architecture with four primary layers:

- **API layer:** HTTP routing, authentication, validation, serialization, and error mapping.
- **Application layer:** Question-answering orchestration and routing policies.
- **Domain layer:** Provider-independent models, values, and exceptions.
- **Infrastructure layer:** PostgreSQL/pgvector persistence and LangChain/OpenAI adapters.

Application logic depends on typed interfaces such as `EmbeddingProvider`, `FaqRepository`, `AnswerGenerator`, `InputGuard`, and `DomainRouter`. This keeps business logic independent of specific AI providers, databases, and frameworks.

The main use case is coordinated by `QuestionAnsweringService`, which can be tested entirely with deterministic fakes without making live API calls.

### Semantic retrieval and routing

FAQ embeddings are precomputed and persisted in PostgreSQL using pgvector. At runtime, only the incoming question needs to be embedded.

The retrieval policy examines the two most similar records. A local answer is accepted only when:

- The highest similarity meets the configured threshold.
- The difference between the first and second results meets the configured ambiguity margin.

This reduces the risk of returning an incorrect local answer when two FAQ entries represent similar or overlapping intents.

The threshold and ambiguity margin are configuration values rather than hardcoded assumptions. In a production deployment, they should be calibrated against a representative, version-controlled evaluation dataset.

### Knowledge-base synchronization

The repository includes an incremental embedding synchronization script.

Each FAQ record receives a content hash derived from its normalized question, answer, category, and embedding model. Unchanged records are not embedded again, reducing external API usage, execution time, and cost.

The database also records the embedding model and vector dimensions. This prevents accidental comparisons between vectors generated from incompatible embedding spaces.

Invalid or unusable knowledge-base records are excluded from semantic retrieval. A future production version would additionally place rejected records into a formal quarantine report for review.

### Security considerations

The implementation applies defense in depth:

- Bearer-token authentication.
- Constant-time credential comparison.
- Strict Pydantic request validation.
- Maximum input length enforcement.
- Detection of common prompt-injection patterns.
- Deterministic routing for unsupported domains.
- A narrowly scoped fallback system prompt.
- Explicit treatment of user input as untrusted data.
- Provider timeouts and bounded retries.
- Sanitized error responses.
- No secrets or internal database context included in prompts.
- Environment-based secret configuration.
- Non-root Docker execution.

Regex-based detection is not presented as a complete solution to prompt injection. It is an initial defensive layer that can later be supplemented by structured policy classification, output moderation, data-loss-prevention checks, rate limiting, and adversarial evaluation.

### Testing and quality assurance

The implementation includes deterministic tests for:

- Confident local FAQ matches.
- Low-similarity fallback routing.
- Ambiguous retrieval results.
- Unsupported-domain routing.
- Prompt-injection rejection.
- Authentication enforcement.
- API request and response behavior.
- Provider-independent application orchestration.

Tests use dependency injection and fakes rather than live OpenAI requests. This makes the test suite fast, repeatable, and suitable for continuous integration.

The CI pipeline enforces:

- Ruff formatting.
- Ruff linting.
- Strict mypy type checking.
- Pytest execution.
- Code-coverage requirements.

Quality assurance is treated as an SDLC concern rather than only a testing phase. The included documentation describes acceptance criteria, static analysis, unit testing, integration testing, provider contract testing, AI evaluation, security testing, deployment gates, monitoring, and rollback expectations.

### AI evaluation strategy

The proposed evaluation process separates retrieval, routing, generated-answer quality, safety, performance, and cost.

Recommended objective metrics include:

- Recall@1 and Recall@K.
- Mean Reciprocal Rank.
- Routing accuracy, precision, recall, and F1.
- Local false-match rate.
- Local false-rejection rate.
- Out-of-domain precision.
- Prompt-injection refusal rate.
- Provider error rate.
- p50, p95, and p99 latency.
- Cost per request.

Fallback answers should also receive human evaluation for relevance, factuality, helpfulness, conciseness, safety, policy adherence, and unsupported claims.

A version-controlled golden dataset should include direct FAQ paraphrases, informal language, spelling errors, near-neighbor questions, unsupported requests, multi-intent questions, expected fallback cases, and adversarial prompts.

### Operational behavior

Expected API behavior includes:

- `200` for successful local, fallback, and compliance responses.
- `400` for recognized unsafe instructions.
- `401` for missing or invalid authentication.
- `422` for malformed requests.
- `503` when the external answer provider is unavailable.

The repository includes:

- A multi-stage Dockerfile.
- Docker Compose configuration.
- A local pgvector database.
- Automatic knowledge-base synchronization.
- Environment-based configuration.
- Health and question-answering endpoints.
- GitHub Actions continuous integration.
- Architecture, security, evaluation, testing, SDLC, and roadmap documentation.

### Design trade-offs

Several choices were intentionally kept simple for the current dataset and challenge scope:

- **Direct local answers:** Stored FAQ answers are returned unchanged to avoid unnecessary model cost and hallucination risk.
- **Deterministic first-line domain routing:** A keyword router provides fast, explainable filtering and can later be replaced without changing the orchestration service.
- **Exact vector search:** Appropriate for the current knowledge-base size. An HNSW index can be introduced when scale justifies approximate nearest-neighbor search.
- **Synchronous fallback flow:** Suitable for interactive API requests, with timeouts protecting availability.
- **Script-based ingestion:** Appropriate for a small knowledge base. Celery or another durable queue can be introduced for high-volume or event-driven ingestion.
- **Ports instead of provider coupling:** Infrastructure components can be replaced independently without rewriting core business logic.

### Scalability roadmap

The architecture supports incremental evolution toward:

- Alembic-managed database migrations.
- Hybrid lexical and semantic retrieval.
- Cross-encoder reranking.
- Category-aware retrieval.
- Calibrated thresholds by intent or category.
- Structured-output domain classification.
- HNSW vector indexes.
- Celery-based ingestion workers.
- Batch embedding generation.
- Dead-letter queues and ingestion retries.
- Multiple or tenant-specific collections.
- Redis caching.
- PgBouncer and managed PostgreSQL.
- Horizontal API scaling.
- OpenTelemetry tracing.
- Prometheus metrics.
- Structured JSON logging.
- API gateway authentication and rate limiting.
- Managed secrets and restricted provider egress.
- Canary deployments and automated rollback.

### Running the project

1. Copy the example configuration:

   ```bash
   cp .env.example .env

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

2. Configure a secure API token and OpenAI API key:

dotenv

API_TOKEN=replace-with-a-long-random-token
OPENAI_API_KEY=your-openai-api-key

3. Start the complete environment:

bash

docker compose up --build


4. Open the interactive API documentation:

text

http://localhost:8000/docs


5. Submit a question:

bash

curl -X POST http://localhost:8000/v1/questions \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"How can I reset my password?"}'
  
  
Local quality checks

bash

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

ruff format --check .
ruff check .
mypy src
pytest --cov=semantic_faq --cov-report=term-missing


### Local quality checks

bash

python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

ruff format --check .
ruff check .
mypy src
pytest --cov=semantic_faq --cov-report=term-missing

