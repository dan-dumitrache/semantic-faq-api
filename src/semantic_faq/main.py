import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from semantic_faq.api.routes import router
from semantic_faq.application.routing import (
    KeywordDomainRouter,
    RegexInputGuard,
    SimilarityRoutingPolicy,
)
from semantic_faq.application.service import QuestionAnsweringService
from semantic_faq.config import get_settings
from semantic_faq.domain import ProviderUnavailableError, UnsafeInputError
from semantic_faq.infrastructure.database import create_engine, create_session_factory
from semantic_faq.infrastructure.langchain_providers import (
    LangChainAnswerGenerator,
    LangChainEmbeddingProvider,
)
from semantic_faq.infrastructure.repository import PgVectorFaqRepository


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    engine = create_engine(settings.database_url)
    sessions = create_session_factory(engine)

    embeddings = LangChainEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        dimensions=settings.embedding_dimensions,
    )
    generator = LangChainAnswerGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )

    app.state.qa_service = QuestionAnsweringService(
        embeddings=embeddings,
        repository=PgVectorFaqRepository(sessions),
        answer_generator=generator,
        input_guard=RegexInputGuard(settings.max_question_length),
        domain_router=KeywordDomainRouter(),
        routing_policy=SimilarityRoutingPolicy(
            minimum_similarity=settings.local_match_threshold,
            ambiguity_margin=settings.ambiguity_margin,
        ),
        collection=settings.faq_collection,
    )
    app.state.engine = engine

    yield

    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Semantic FAQ API",
        version="1.0.0",
        description="Semantic FAQ retrieval with guarded OpenAI fallback.",
        lifespan=lifespan,
    )

    app.include_router(router)

    @app.exception_handler(UnsafeInputError)
    async def unsafe_input_handler(
        _: Request,
        exc: UnsafeInputError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ProviderUnavailableError)
    async def provider_error_handler(
        _: Request,
        exc: ProviderUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    return app


app = create_app()