from semantic_faq.application.ports import (
    AnswerGenerator,
    DomainRouter,
    EmbeddingProvider,
    FaqRepository,
    InputGuard,
)
from semantic_faq.application.routing import (
    COMPLIANCE_MESSAGE,
    SimilarityRoutingPolicy,
)
from semantic_faq.domain import Answer, AnswerSource, ProviderUnavailableError


class QuestionAnsweringService:
    def __init__(
        self,
        *,
        embeddings: EmbeddingProvider,
        repository: FaqRepository,
        answer_generator: AnswerGenerator,
        input_guard: InputGuard,
        domain_router: DomainRouter,
        routing_policy: SimilarityRoutingPolicy,
        collection: str,
    ) -> None:
        self._embeddings = embeddings
        self._repository = repository
        self._answer_generator = answer_generator
        self._input_guard = input_guard
        self._domain_router = domain_router
        self._routing_policy = routing_policy
        self._collection = collection

    async def answer(self, question: str) -> Answer:
        question = question.strip()
        self._input_guard.validate(question)

        if not self._domain_router.is_supported(question):
            return Answer(
                source=AnswerSource.COMPLIANCE,
                matched_question=None,
                answer=COMPLIANCE_MESSAGE,
            )

        embedding = await self._embeddings.embed_query(question)
        candidates = await self._repository.search(
            embedding,
            collection=self._collection,
            limit=2,
        )
        decision = self._routing_policy.decide(candidates)

        if decision.use_local and decision.candidate is not None:
            candidate = decision.candidate
            return Answer(
                source=AnswerSource.LOCAL,
                matched_question=candidate.question,
                answer=candidate.answer,
                similarity=candidate.similarity,
            )

        try:
            generated = (await self._answer_generator.generate(question)).strip()
        except Exception as exc:
            raise ProviderUnavailableError(
                "The answer provider is temporarily unavailable."
            ) from exc

        if not generated:
            raise ProviderUnavailableError("The answer provider returned an empty response.")

        return Answer(
            source=AnswerSource.OPENAI,
            matched_question=None,
            answer=generated,
        )