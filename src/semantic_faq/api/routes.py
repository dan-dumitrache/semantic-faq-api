from fastapi import APIRouter

from semantic_faq.api.dependencies import Authenticated, QaService
from semantic_faq.api.schemas import AnswerResponse, HealthResponse, QuestionRequest

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["operations"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post(
    "/v1/questions",
    response_model=AnswerResponse,
    tags=["questions"],
)
async def ask_question(
    payload: QuestionRequest,
    _: Authenticated,
    service: QaService,
) -> AnswerResponse:
    result = await service.answer(payload.question)

    return AnswerResponse(
        source=result.source.value,
        matched_question=result.matched_question or "N/A",
        answer=result.answer,
        similarity=result.similarity,
    )