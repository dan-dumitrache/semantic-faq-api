## AI/ML evaluation

Evaluation separates retrieval quality, routing quality, answer quality,
security, latency, and cost.

### Evaluation dataset

Create a version-controlled dataset containing:

- Direct paraphrases of each FAQ
- Informal language and typographical errors
- Multi-intent questions
- Near-neighbor questions
- Unsupported questions
- Prompt-injection attempts
- Queries for which OpenAI fallback is expected
- Questions that should not match low-quality FAQ records

Each example should have labels for:

- Expected route
- Expected FAQ identifier, if applicable
- Acceptable answer facts
- Forbidden claims
- Safety expectation

Use separate development and holdout sets. Tune thresholds only on the
development set.

### Objective metrics

| Component | Metrics |
|---|---|
| Retrieval | Recall@1, Recall@K, MRR |
| Routing | Accuracy, precision, recall, F1, confusion matrix |
| Local acceptance | False-match and false-rejection rates |
| Domain routing | In-domain recall, out-of-domain precision |
| Reliability | Provider failure rate, HTTP error rate |
| Performance | p50, p95, p99 latency |
| Cost | Embedding and completion cost per request |
| Security | Attack refusal rate and benign false-positive rate |

False local matches deserve special attention because returning an incorrect
company-specific answer may be worse than escalating to a fallback.

### Subjective answer evaluation

Reviewers score fallback answers from 1–5 for:

- Relevance
- Factuality
- Helpfulness
- Conciseness
- Safety
- Policy adherence
- Unsupported-claim avoidance

Use two reviewers for a sample and investigate large disagreements. LLM judges
may assist with regression screening but should not be the sole authority.

### Release criteria

An example release gate:

- Retrieval Recall@1 >= 90% on supported FAQ paraphrases
- Out-of-domain precision >= 95%
- Local false-match rate <= 2%
- Prompt-injection refusal rate >= 95% on the attack suite
- No critical safety failures
- p95 local-response latency within the agreed service objective
