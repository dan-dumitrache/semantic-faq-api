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
