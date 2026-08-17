### `docs/architecture.md`

```markdown
## Architecture

The project follows ports-and-adapters principles without adding a large
framework.

### Layers

- **API:** HTTP validation, authentication, and response serialization.
- **Application:** use-case orchestration and routing policies.
- **Domain:** provider-independent records, values, and exceptions.
- **Infrastructure:** PostgreSQL, pgvector, LangChain, and OpenAI adapters.

The application layer owns the interfaces. Infrastructure depends inward on
those interfaces; business logic does not import provider-specific classes.

### Retrieval decision

The database returns the top two candidates. A local answer is accepted when:

1. The best result meets the configured similarity threshold.
2. Its score exceeds the second result by the configured ambiguity margin.

The second condition reduces false-positive routing between near-duplicate
intents, such as changing an email versus verifying an email.

Thresholds are not universal constants. They must be calibrated against an
evaluation dataset generated with the exact embedding model and real user
queries.

### Failure behavior

- Invalid input: HTTP 422
- Recognized exploitative input: HTTP 400
- Authentication failure: HTTP 401
- External AI provider failure: HTTP 503
- Out-of-domain input: HTTP 200 with deterministic compliance response

A production deployment should add request identifiers, JSON logs, metrics,
distributed tracing, and a global handler that returns a generic HTTP 500
without exposing internal details.
