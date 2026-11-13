"""Local multilingual Sentence Transformers adapter; no mock-vector fallback."""
from __future__ import annotations

import os
from typing import Protocol


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, question: str) -> list[float]: ...


class MyEmbedder:
    """Use one real local model for document and query vectors."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Local embeddings require sentence-transformers. Install it with "
                "`python -m pip install -r requirements-embeddings.txt`."
            ) from exc

        device = os.getenv("EMBEDDING_DEVICE", "cpu")
        try:
            self._model = SentenceTransformer(self.model_name, device=device)
            dimensions = self._model.get_sentence_embedding_dimension()
        except Exception as exc:
            raise RuntimeError(
                f"Could not load embedding model {self.model_name!r} on {device!r}; "
                "check model name, network access, and available memory."
            ) from exc
        if not dimensions:
            raise RuntimeError(f"Model {self.model_name!r} did not report an embedding dimension")
        self.dimensions = int(dimensions)
        self._batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
        if self._batch_size < 1:
            raise ValueError("EMBEDDING_BATCH_SIZE must be at least 1")

    def _encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(
            texts,
            batch_size=self._batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        vectors = [[float(value) for value in row] for row in embeddings]
        if len(vectors) != len(texts):
            raise RuntimeError(f"Embedding count mismatch: expected {len(texts)}, got {len(vectors)}")
        for vector in vectors:
            if len(vector) != self.dimensions:
                raise RuntimeError(
                    f"Embedding dimension mismatch: expected {self.dimensions}, got {len(vector)}"
                )
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def embed_query(self, question: str) -> list[float]:
        vectors = self._encode([question])
        return vectors[0]
