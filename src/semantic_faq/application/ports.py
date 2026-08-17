from typing import Protocol

from semantic_faq.domain import FaqCandidate


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str:
        ...

    @property
    def dimensions(self) -> int:
        ...

    async def embed_query(self, text: str) -> list[float]:
        ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...


class FaqRepository(Protocol):
    async def search(
        self,
        embedding: list[float],
        *,
        collection: str,
        limit: int = 2,
    ) -> list[FaqCandidate]:
        ...


class AnswerGenerator(Protocol):
    async def generate(self, question: str) -> str:
        ...


class InputGuard(Protocol):
    def validate(self, question: str) -> None:
        ...


class DomainRouter(Protocol):
    def is_supported(self, question: str) -> bool:
        ...