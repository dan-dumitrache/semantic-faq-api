import re
from dataclasses import dataclass

from semantic_faq.domain import FaqCandidate, UnsafeInputError

COMPLIANCE_MESSAGE = (
    "This is not really what I was trained for, therefore I cannot answer. Try again."
)

_SUPPORTED_TERMS = {
    "account",
    "api",
    "app",
    "avatar",
    "billing",
    "crash",
    "data",
    "email",
    "invoice",
    "login",
    "notification",
    "passkey",
    "password",
    "payment",
    "phishing",
    "plan",
    "privacy",
    "profile",
    "refund",
    "security",
    "session",
    "subscription",
    "two-factor",
    "2fa",
}

_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"(reveal|show|print)\s+(the\s+)?(system|developer)\s+prompt", re.IGNORECASE),
    re.compile(r"bypass\s+(security|guardrails|policy)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(an?\s+)?unrestricted", re.IGNORECASE),
)


class RegexInputGuard:
    def __init__(self, max_length: int) -> None:
        self._max_length = max_length

    def validate(self, question: str) -> None:
        normalized = question.strip()

        if not normalized:
            raise UnsafeInputError("Question must not be empty.")

        if len(normalized) > self._max_length:
            raise UnsafeInputError("Question exceeds the maximum permitted length.")

        if any(pattern.search(normalized) for pattern in _INJECTION_PATTERNS):
            raise UnsafeInputError("The question contains unsupported instructions.")


class KeywordDomainRouter:
    """Cheap deterministic first-line router.

    Semantic retrieval remains the final in-domain signal. This router prevents
    clearly unrelated requests from unnecessarily reaching an external model.
    """

    def is_supported(self, question: str) -> bool:
        words = set(re.findall(r"[a-z0-9-]+", question.lower()))
        return bool(words & _SUPPORTED_TERMS)


@dataclass(frozen=True, slots=True)
class MatchDecision:
    use_local: bool
    candidate: FaqCandidate | None
    reason: str


@dataclass(frozen=True, slots=True)
class SimilarityRoutingPolicy:
    minimum_similarity: float
    ambiguity_margin: float

    def decide(self, candidates: list[FaqCandidate]) -> MatchDecision:
        if not candidates:
            return MatchDecision(False, None, "no_candidates")

        best = candidates[0]

        if best.similarity < self.minimum_similarity:
            return MatchDecision(False, best, "below_threshold")

        if len(candidates) > 1:
            margin = best.similarity - candidates[1].similarity
            if margin < self.ambiguity_margin:
                return MatchDecision(False, best, "ambiguous_match")

        return MatchDecision(True, best, "confident_match")
