from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from semantic_faq.domain import FaqCandidate


class PgVectorFaqRepository:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def search(
        self,
        embedding: list[float],
        *,
        collection: str,
        limit: int = 2,
    ) -> list[FaqCandidate]:
        vector = "[" + ",".join(str(value) for value in embedding) + "]"

        statement = text(
            """
            SELECT
                id,
                question,
                answer,
                category,
                1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM faq_items
            WHERE collection = :collection
              AND active = TRUE
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )

        async with self._sessions() as session:
            rows = (
                await session.execute(
                    statement,
                    {
                        "embedding": vector,
                        "collection": collection,
                        "limit": limit,
                    },
                )
            ).mappings()

            return [
                FaqCandidate(
                    id=row["id"],
                    question=row["question"],
                    answer=row["answer"],
                    category=row["category"],
                    similarity=float(row["similarity"]),
                )
                for row in rows
            ]
