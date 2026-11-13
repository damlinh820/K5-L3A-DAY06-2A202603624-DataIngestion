"""Read and normalize source data while preserving physical page references."""
from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentPage

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Normalize Unicode and whitespace while preserving paragraph boundaries."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[\t\f\v ]+", " ", line).strip() for line in text.split("\n")]

    normalized: list[str] = []
    previous_blank = True
    for line in lines:
        if not line:
            if not previous_blank:
                normalized.append("")
            previous_blank = True
            continue
        normalized.append(line)
        previous_blank = False
    while normalized and not normalized[-1]:
        normalized.pop()
    return "\n".join(normalized).strip()


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; empty pages are logged and retained."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}. Put it under starter/data or fix manifest.json.")

    reader = PdfReader(str(path))
    pages: list[DocumentPage] = []
    for page_number, pdf_page in enumerate(reader.pages, start=1):
        try:
            text = normalize_text(pdf_page.extract_text() or "")
        except Exception as exc:  # keep the physical page number in diagnostics
            logger.exception("Failed extracting %s page %d", path.name, page_number)
            text = ""
            error = str(exc)
        else:
            error = None

        metadata = {"local_path": path.as_posix()}
        if error:
            metadata["extraction_error"] = error
        if not text:
            logger.warning("No extractable text: %s page %d", path.name, page_number)
            metadata["empty_page"] = True
        pages.append(DocumentPage(
            document_id=document_id,
            source=source,
            page=page_number,
            text=text,
            metadata=metadata,
        ))
    return pages
