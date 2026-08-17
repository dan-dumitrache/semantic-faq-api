from dataclasses import dataclass
from enum import StrEnum


class AnswerSource(StrEnum):
    LOCAL = "local"
    OPENAI = "openai"
    COMPLIANCE = "compliance"


@dataclass(frozen=True, slots=True)
class FaqCandidate:
    id: int
    question: str
    answer: str
    category: str
    similarity: float


@dataclass(frozen=True, slots=True)
class Answer:
    source: AnswerSource
    matched_question: str | None
    answer: str
    similarity: float | None = None


class ApplicationError(Exception):
    """Base exception for expected application failures."""


class ProviderUnavailableError(ApplicationError):
    """Raised when an external AI provider is unavailable."""


class UnsafeInputError(ApplicationError):
    """Raised when input violates a security policy."""