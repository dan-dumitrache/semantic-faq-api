## Future development roadmap

### Near term

- Add Alembic migrations instead of script-managed schema creation
- Add structured JSON logging and request IDs
- Add PostgreSQL integration tests using Testcontainers
- Add an evaluation CLI and versioned golden dataset
- Add Prometheus metrics and OpenTelemetry tracing
- Add rate limiting
- Add quarantine reports for rejected knowledge-base records

### Retrieval improvements

- Hybrid lexical and semantic retrieval
- Category-aware filtering
- Cross-encoder reranking
- Multi-query retrieval for unclear inputs
- Calibrated category-specific thresholds
- HNSW pgvector index after the dataset grows
- Retrieval explanations stored in internal telemetry
- Duplicate and contradiction detection during ingestion

### Router improvements

Replace the keyword domain router with a staged router:

1. Deterministic security rules
2. Lightweight semantic domain classifier
3. Structured-output LLM classifier only for ambiguous cases
4. Retrieval confidence policy
5. Compliance, local-answer, or fallback route

The classifier must return validated enums rather than arbitrary tool calls.

### Ingestion scalability

- Celery or another durable queue
- Batch embedding requests
- Retry queues and dead-letter handling
- Scheduled data synchronization
- Multiple collections and collection aliases
- Zero-downtime collection replacement
- Object storage for raw source artifacts
- Event-driven updates
- Per-tenant collections and authorization

### Platform scalability

- PgBouncer
- Managed PostgreSQL
- Redis caching
- Horizontal API replicas
- Kubernetes
- Managed secret storage
- Regional deployment
- Usage quotas and cost budgets

### Governance

- Dataset and prompt versioning
- Model cards and evaluation reports
- PII classification and retention policy
- Human approval for sensitive knowledge changes
- Audit trails
- Incident response playbooks
- Model/provider upgrade procedures
