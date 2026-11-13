"""Persistent PostgreSQL + pgvector storage with metadata-filtered cosine search."""
from __future__ import annotations

import json
import math
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from .models import Chunk


def _vector_literal(vector: list[float]) -> str:
    if not vector or any(not math.isfinite(float(x)) for x in vector):
        raise ValueError("Vectors must be non-empty and contain only finite numbers")
    return "[" + ",".join(format(float(x), ".9g") for x in vector) + "]"


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL is required")
        if dimensions < 1:
            raise ValueError("Embedding dimensions must be positive")
        self.database_url = database_url
        self.dimensions = dimensions

    def create_schema(self) -> None:
        try:
            with psycopg.connect(self.database_url) as conn:
                conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS day6_chunks (
                        strategy TEXT NOT NULL,
                        chunk_id TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        source TEXT NOT NULL,
                        page INTEGER NOT NULL,
                        text TEXT NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                        embedding vector NOT NULL,
                        PRIMARY KEY (strategy, chunk_id)
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS day6_chunks_strategy_idx ON day6_chunks (strategy)"
                )
        except psycopg.Error as exc:
            raise RuntimeError(
                "Could not initialize pgvector. Start the provided Docker database and "
                "check DATABASE_URL and the pgvector extension."
            ) from exc

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"Chunk/vector count mismatch: {len(chunks)} != {len(vectors)}")
        rows = []
        for chunk, vector in zip(chunks, vectors):
            if len(vector) != self.dimensions:
                raise ValueError(
                    f"Chunk {chunk.chunk_id} has {len(vector)} dimensions; expected {self.dimensions}"
                )
            rows.append((
                strategy,
                chunk.chunk_id,
                chunk.document_id,
                chunk.source,
                chunk.page,
                chunk.text,
                Jsonb(chunk.metadata),
                _vector_literal(vector),
            ))

        # Replace one strategy atomically. This removes stale chunks on re-ingestion;
        # a failed insert rolls the delete back with the transaction.
        with psycopg.connect(self.database_url) as conn:
            with conn.transaction():
                conn.execute("DELETE FROM day6_chunks WHERE strategy = %s", (strategy,))
                if rows:
                    with conn.cursor() as cursor:
                        cursor.executemany(
                            """
                            INSERT INTO day6_chunks
                                (strategy, chunk_id, document_id, source, page, text, metadata, embedding)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                            ON CONFLICT (strategy, chunk_id) DO UPDATE SET
                                document_id = EXCLUDED.document_id,
                                source = EXCLUDED.source,
                                page = EXCLUDED.page,
                                text = EXCLUDED.text,
                                metadata = EXCLUDED.metadata,
                                embedding = EXCLUDED.embedding
                            """,
                            rows,
                        )

    def search(
        self,
        strategy: str,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if len(query_vector) != self.dimensions:
            raise ValueError(
                f"Query has {len(query_vector)} dimensions; expected {self.dimensions}"
            )
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        clauses = ["strategy = %s"]
        params: list[Any] = [strategy]
        for key, value in (filters or {}).items():
            if not isinstance(key, str) or not key:
                raise ValueError("Filter keys must be non-empty strings")
            clauses.append("metadata ->> %s = %s")
            params.extend((key, str(value)))
        vector = _vector_literal(query_vector)
        params.extend((vector, top_k))
        where_sql = " AND ".join(clauses)

        with psycopg.connect(self.database_url) as conn:
            rows = conn.execute(
                f"""
                SELECT chunk_id, document_id, source, page, text, metadata,
                       1 - (embedding <=> %s::vector) AS score
                FROM day6_chunks
                WHERE {where_sql}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vector, *params[:-2], vector, top_k),
            ).fetchall()

        results = []
        for chunk_id, document_id, source, page, text, metadata, score in rows:
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            results.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "source": source,
                "page": page,
                "text": text,
                "metadata": metadata,
                "score": float(score),
            })
        return results
