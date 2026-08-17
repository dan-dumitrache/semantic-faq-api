import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from sqlalchemy import text

from semantic_faq.config import get_settings
from semantic_faq.infrastructure.database import create_engine
from semantic_faq.infrastructure.langchain_providers import LangChainEmbeddingProvider

DATA_PATH = Path("data/knowledge_base.json")


def normalize_question(value: str) -> str:
    return " ".join(value.strip().split())


def content_hash(item: dict[str, Any], model: str) -> str:
    payload = "|".join(
        [
            normalize_question(str(item["question"])),
            str(item["answer"]).strip(),
            str(item["category"]).strip(),
            model,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_items() -> list[dict[str, Any]]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    items: list[dict[str, Any]] = data["knowledge_base_items"]

    # Quarantine intentionally unusable records instead of embedding them.
    return [
        item
        for item in items
        if len(normalize_question(str(item["question"]))) >= 3
        and len(str(item["answer"]).strip()) >= 10
    ]


async def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    provider = LangChainEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        dimensions=settings.embedding_dimensions,
    )

    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS faq_items (
                    id BIGSERIAL PRIMARY KEY,
                    collection TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content_hash CHAR(64) NOT NULL,
                    embedding_model TEXT NOT NULL,
                    embedding_dimensions INTEGER NOT NULL,
                    embedding vector({settings.embedding_dimensions}) NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (collection, content_hash)
                )
                """
            )
        )
        await connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_faq_collection
                ON faq_items (collection)
                """
            )
        )

    items = load_items()
    hashes = [content_hash(item, provider.model_name) for item in items]

    async with engine.connect() as connection:
        existing_rows = await connection.execute(
            text(
                """
                SELECT content_hash
                FROM faq_items
                WHERE collection = :collection
                  AND content_hash = ANY(:hashes)
                """
            ),
            {"collection": settings.faq_collection, "hashes": hashes},
        )
        existing = {row[0] for row in existing_rows}

    pending = [
        (item, item_hash)
        for item, item_hash in zip(items, hashes, strict=True)
        if item_hash not in existing
    ]

    if not pending:
        print("Knowledge base is already synchronized.")
        await engine.dispose()
        return

    embeddings = await provider.embed_documents(
        [normalize_question(str(item["question"])) for item, _ in pending]
    )

    async with engine.begin() as connection:
        for (item, item_hash), embedding in zip(pending, embeddings, strict=True):
            vector = "[" + ",".join(str(value) for value in embedding) + "]"
            await connection.execute(
                text(
                    """
                    INSERT INTO faq_items (
                        collection,
                        question,
                        answer,
                        category,
                        content_hash,
                        embedding_model,
                        embedding_dimensions,
                        embedding
                    )
                    VALUES (
                        :collection,
                        :question,
                        :answer,
                        :category,
                        :content_hash,
                        :embedding_model,
                        :dimensions,
                        CAST(:embedding AS vector)
                    )
                    ON CONFLICT (collection, content_hash) DO NOTHING
                    """
                ),
                {
                    "collection": settings.faq_collection,
                    "question": normalize_question(str(item["question"])),
                    "answer": str(item["answer"]).strip(),
                    "category": str(item["category"]).strip(),
                    "content_hash": item_hash,
                    "embedding_model": provider.model_name,
                    "dimensions": provider.dimensions,
                    "embedding": vector,
                },
            )

    print(f"Inserted {len(pending)} new or changed FAQ items.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
