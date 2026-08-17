## QA strategy across the SDLC

Quality assurance begins during requirements definition rather than after
implementation.

### 1. Requirements and acceptance testing

Convert requirements into traceable acceptance criteria:

- A confident FAQ match returns the stored answer.
- A low-confidence in-domain question reaches the fallback provider.
- An unrelated question returns the exact compliance response.
- Missing authentication returns HTTP 401.
- Malformed requests return HTTP 422.
- Provider failure returns a sanitized HTTP 503.
- No unit test makes a live OpenAI request.
- Changed FAQ records are re-embedded; unchanged records are not.

Maintain a requirement-to-test traceability list in pull requests or the issue
tracker.

### 2. Static quality gates

Every pull request runs:

- Ruff formatting verification
- Ruff linting
- Strict mypy checking
- Unit and API tests
- Coverage threshold

Future gates should include Bandit, pip-audit, container scanning, and secret
scanning.

### 3. Unit tests

Unit tests isolate:

- Similarity threshold behavior
- Ambiguity margins
- Domain routing
- Input guards
- Local answer selection
- OpenAI fallback selection
- Empty and malformed provider output
- Provider exceptions

Fakes are preferred to patching LangChain internals.

### 4. Integration tests

Integration tests cover:

- FastAPI serialization and validation
- Authentication dependencies
- Error mapping
- PostgreSQL vector retrieval
- Schema creation and synchronization behavior

Database integration tests should use a temporary pgvector container.

### 5. Contract tests

Provider adapters should have optional contract tests confirming that:

- Embeddings have the configured dimensions.
- Chat responses can be parsed as text.
- Timeout behavior is mapped correctly.

These tests use live APIs only when explicitly enabled and are excluded from
ordinary CI.

### 6. AI evaluation tests

A versioned golden dataset evaluates retrieval, routing, security, and answer
quality. Threshold changes and embedding-model upgrades require comparison
against the previous baseline.

### 7. System and non-functional tests

Before production:

- Load and concurrency testing
- Timeout and dependency-failure testing
- Database recovery testing
- Rate-limit verification
- Container security testing
- Observability verification
- Backup and restore exercises

### 8. Deployment and operations

Recommended flow:

1. Feature branch and pull request
2. Automated quality gates
3. Review by at least one engineer
4. Deploy to staging
5. Run smoke and AI regression tests
6. Canary or gradual production release
7. Monitor errors, route distribution, latency, and cost
8. Roll back automatically on service-level objective violations

### Test pyramid

The project should contain many fast unit tests, fewer database/API integration
tests, and a small number of expensive end-to-end or live-provider tests.

Coverage is a useful signal, not proof of correctness. Branch behavior,
requirement coverage, and adversarial evaluation matter more than maximizing a
single percentage.
