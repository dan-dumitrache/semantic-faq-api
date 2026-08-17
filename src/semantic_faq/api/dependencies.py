import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from semantic_faq.application.service import QuestionAnsweringService
from semantic_faq.config import Settings, get_settings


def verify_token(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    expected = f"Bearer {settings.api_token}"

    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_qa_service(request: Request) -> QuestionAnsweringService:
    service: QuestionAnsweringService = request.app.state.qa_service
    return service


Authenticated = Annotated[None, Depends(verify_token)]
QaService = Annotated[QuestionAnsweringService, Depends(get_qa_service)]