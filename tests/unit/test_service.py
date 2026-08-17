from semantic_faq.application.routing import SimilarityRoutingPolicy
from semantic_faq.application.service import QuestionAnsweringService
from semantic_faq.domain import AnswerSource, FaqCandidate


class FakeEmbeddings:
    model_name = "fake"
    dimensions = 3

    async def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeRepository:
    def __init__(self, candidates: list[FaqCandidate]) -> None:
        self.candidates = candidates

    async def search(
        self,
        embedding: list[float],
        *,
        collection: str,
        limit: int = 2,
    ) -> list[FaqCandidate]:
        return self.candidates[:limit]


class FakeGenerator:
    async def generate(self, question: str) -> str:
        return "Generated fallback answer."


class AllowGuard:
    def validate(self, question: str) -> None:
        return None


class SupportedRouter:
    def is_supported(self, question: str) -> bool:
        return True


class UnsupportedRouter:
    def is_supported(self, question: str) -> bool:
        return False


def build_service(
    candidates: list[FaqCandidate],
    *,
    supported: bool = True,
) -> QuestionAnsweringService:
    return QuestionAnsweringService(
        embeddings=FakeEmbeddings(),
        repository=FakeRepository(candidates),
        answer_generator=FakeGenerator(),
        input_guard=AllowGuard(),
        domain_router=SupportedRouter() if supported else UnsupportedRouter(),
        routing_policy=SimilarityRoutingPolicy(0.78, 0.03),
        collection="test",
    )


async def test_returns_local_answer_for_confident_match() -> None:
    match = FaqCandidate(
        id=1,
        question="How do I reset my password?",
        answer="Open account settings.",
        category="security",
        similarity=0.95,
    )

    result = await build_service([match]).answer("Reset password")

    assert result.source == AnswerSource.LOCAL
    assert result.answer == "Open account settings."
    assert result.matched_question == match.question


async def test_uses_fallback_for_low_similarity() -> None:
    match = FaqCandidate(
        id=1,
        question="How do I reset my password?",
        answer="Open account settings.",
        category="security",
        similarity=0.55,
    )

    result = await build_service([match]).answer("Account question")

    assert result.source == AnswerSource.OPENAI
    assert result.matched_question is None


async def test_returns_compliance_response_for_unsupported_domain() -> None:
    result = await build_service([], supported=False).answer("Write a poem")

    assert result.source == AnswerSource.COMPLIANCE
    assert "not really what I was trained for" in result.answer

'tests/integration/test_api.py'

python

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

os.environ.setdefault("API_TOKEN", "test-token-with-minimum-length")
os.environ.setdefault("OPENAI_API_KEY", "not-used")

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from semantic_faq.api.dependencies import get_qa_service
from semantic_faq.domain import Answer, AnswerSource
from semantic_faq.main import create_app


class FakeService:
    async def answer(self, question: str) -> Answer:
        return Answer(
            source=AnswerSource.LOCAL,
            matched_question="How do I reset my password?",
            answer="Use account settings.",
            similarity=0.93,
        )


@asynccontextmanager
async def no_lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield


async def test_question_endpoint() -> None:
    app = create_app()
    app.router.lifespan_context = no_lifespan
    app.dependency_overrides[get_qa_service] = lambda: FakeService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/questions",
            headers={"Authorization": "Bearer test-token-with-minimum-length"},
            json={"question": "How can I reset my password?"},
        )

    assert response.status_code == 200
    assert response.json()["source"] == "local"
    assert response.json()["similarity"] == 0.93


async def test_question_endpoint_requires_authentication() -> None:
    app = create_app()
    app.router.lifespan_context = no_lifespan
    app.dependency_overrides[get_qa_service] = lambda: FakeService()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/questions",
            json={"question": "How can I reset my password?"},
        )

    assert response.status_code == 401
