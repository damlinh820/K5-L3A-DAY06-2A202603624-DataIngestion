"""Deterministic fixed-window and paragraph-aware chunking."""
from __future__ import annotations

import hashlib
import re

from .models import Chunk, DocumentPage


def _make_chunk(page: DocumentPage, text: str, index: int) -> Chunk:
    stable_key = f"{page.document_id}\0{page.page}\0{index}\0{text}"
    chunk_id = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()[:24]
    return Chunk(
        chunk_id=chunk_id,
        document_id=page.document_id,
        source=page.source,
        page=page.page,
        text=text.strip(),
        metadata=dict(page.metadata),
    )


def _split_long(text: str, size: int, overlap: int = 0) -> list[str]:
    if size < 1:
        raise ValueError("size must be at least 1")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and smaller than size")
    if len(text) <= size:
        return [text] if text.strip() else []

    step = size - overlap
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end == len(text):
            break
        start += step
    return pieces


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Split a page into character windows, retaining page and source metadata."""
    return [_make_chunk(page, text, i) for i, text in enumerate(_split_long(page.text, size, overlap))]


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Pack paragraphs up to max_size; sentence-split when PDF extraction flattened them."""
    if max_size < 1:
        raise ValueError("max_size must be at least 1")

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", page.text) if p.strip()]
    if len(paragraphs) <= 1:
        # pypdf often flattens a printed webpage into one long line. Recover sentence
        # boundaries as the next-best semantic units instead of slicing every 1000 chars.
        flattened = re.sub(r"\s+", " ", page.text).strip()
        sentence_units = re.split(
            r"(?<=[.!?])(?:\s*\[[0-9,;\s–-]+\])?\s+(?=[A-ZÀ-ỴĐ“\"(])",
            flattened,
        )
        if len(sentence_units) > 1:
            paragraphs = [unit.strip() for unit in sentence_units if unit.strip()]
    groups: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > max_size:
            if current:
                groups.append(current)
                current = ""
            groups.extend(_split_long(paragraph, max_size))
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_size:
            current = candidate
        else:
            groups.append(current)
            current = paragraph
    if current:
        groups.append(current)

    return [_make_chunk(page, text, i) for i, text in enumerate(groups)]
