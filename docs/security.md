## Security model

User input and model output are untrusted.

### Implemented controls

- Bearer-token authentication through FastAPI dependency injection
- Constant-time token comparison
- Environment-based secret loading
- Strict Pydantic request schema
- Input length limits
- Basic prompt-injection pattern detection
- Deterministic out-of-domain response
- Low-temperature, narrowly scoped fallback prompt
- Delimitation of user input in the prompt
- Provider timeout and bounded retries
- No credentials or database contents included in prompts
- Non-root Docker user

### Limitations

Regexes do not solve prompt injection. They are a defense-in-depth signal.
Obfuscated or novel attacks can bypass keyword-based detection.

Future production controls should include:

- Managed API gateway and identity provider
- Per-principal rate limits and quotas
- TLS termination
- Secret manager instead of local environment files
- Egress restrictions
- Structured-output policy classifier
- Output moderation and data-loss-prevention scanning
- Dependency and container vulnerability scanning
- Audit logging with sensitive-value redaction
- Periodic adversarial test suites
