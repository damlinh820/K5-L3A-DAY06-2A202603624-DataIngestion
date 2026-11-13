"""Orchestrate ingestion and the three Day 06 retrieval strategies."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .chunking import by_paragraph, fixed_size
from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .ingestion import load_pdf
from .models import Chunk, DocumentPage
from .store import PgVectorStore

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
logger = logging.getLogger("day6")


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _manifest_documents(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = _load_json(manifest_path)
    documents = manifest.get("documents") if isinstance(manifest, dict) else None
    if not isinstance(documents, list) or not documents:
        raise ValueError("manifest.json must contain a non-empty 'documents' list")
    return manifest, documents


def _page_numbers(document: dict[str, Any]) -> list[int]:
    values = document.get("content_pages")
    if isinstance(values, list):
        pages = [int(value) for value in values]
    elif isinstance(values, dict) and "start" in values and "end" in values:
        pages = list(range(int(values["start"]), int(values["end"]) + 1))
    else:
        raise ValueError(f"{document.get('document_id', '?')}: set content_pages as a list or start/end")
    if not pages or min(pages) < 1 or len(set(pages)) != len(pages):
        raise ValueError(f"{document.get('document_id', '?')}: content_pages must be unique positive page numbers")
    return pages


def load_corpus(manifest_path: Path) -> tuple[list[DocumentPage], dict[str, Any]]:
    manifest, documents = _manifest_documents(manifest_path)
    all_pages: list[DocumentPage] = []
    page_counts: dict[str, int] = {}
    for document in documents:
        document_id = str(document["document_id"])
        source = str(document["source_path_or_url"])
        local_path = Path(str(document["local_path"]))
        if not local_path.is_absolute():
            local_path = (ROOT / local_path).resolve()
        requested_pages = _page_numbers(document)
        pages = load_pdf(local_path, document_id, source)
        by_number = {page.page: page for page in pages}
        missing_page_ids = sorted(set(requested_pages) - set(by_number))
        if missing_page_ids:
            raise ValueError(f"{document_id}: manifest page numbers not present in PDF: {missing_page_ids}")

        document_metadata = dict(document.get("metadata", {}))
        document_metadata.setdefault("article", document.get("title", document_id))
        selected: list[DocumentPage] = []
        for page_number in requested_pages:
            page = by_number[page_number]
            if not page.text.strip():
                raise ValueError(f"{document_id} page {page_number} has no extractable text")
            page.metadata.update(document_metadata)
            selected.append(page)
        page_counts[document_id] = len(selected)
        all_pages.extend(selected)

    if len(all_pages) < 30:
        raise ValueError(f"Corpus has {len(all_pages)} selected content pages; the minimum is 30")
    if len({(page.document_id, page.page) for page in all_pages}) != len(all_pages):
        raise ValueError("Manifest includes a duplicate document/page pair")
    return all_pages, {"content_pages": len(all_pages), "pages_by_document": page_counts}


def _load_questions(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Benchmark file not found: {path}. Create benchmark/questions.json with verified gold evidence first."
        )
    payload = _load_json(path)
    questions = payload.get("questions") if isinstance(payload, dict) else payload
    if not isinstance(questions, list):
        raise ValueError("Benchmark JSON must be a list or an object with a 'questions' list")
    ids: set[str] = set()
    for question in questions:
        for field in ("id", "split", "question", "expected_answer"):
            if not question.get(field):
                raise ValueError(f"Each benchmark question needs {field!r}: {question}")
        if question["split"] not in {"dev", "test"}:
            raise ValueError(f"Question {question['id']}: split must be 'dev' or 'test'")
        if not isinstance(question.get("filter", {}), dict):
            raise ValueError(f"Question {question['id']}: filter must be a metadata object")
        question_id = str(question["id"])
        if question_id in ids:
            raise ValueError(f"Duplicate benchmark question ID: {question_id}")
        ids.add(question_id)
        # Validate the evidence fields before spending time embedding/indexing.
        if not question.get("gold_evidence") and not all(
            question.get(key) not in (None, "")
            for key in ("gold_source_id", "gold_page", "evidence_quote")
        ):
            raise ValueError(f"Question {question_id} needs gold_evidence or gold source/page/evidence_quote")

    dev_count = sum(question["split"] == "dev" for question in questions)
    test_count = sum(question["split"] == "test" for question in questions)
    filtered = [question for question in questions if question.get("filter")]
    filtered_test = [question for question in filtered if question["split"] == "test"]
    if len(questions) < 20 or dev_count < 15 or test_count < 5:
        raise ValueError(f"Need >=20 questions with >=15 dev and >=5 test; found {len(questions)} ({dev_count}/{test_count})")
    if len(filtered) < 3 or not filtered_test:
        raise ValueError("Need >=3 metadata-filter questions, including >=1 test question")
    return questions


def _make_strategy_chunks(pages: list[DocumentPage]) -> dict[str, list[Chunk]]:
    result: dict[str, list[Chunk]] = {"A": [], "B": [], "C": []}
    for page in pages:
        result["A"].extend(fixed_size(page, size=500, overlap=50))
        paragraph_chunks = by_paragraph(page, max_size=1000)
        result["B"].extend(paragraph_chunks)
        # C is deliberately identical to B; only query-time filtering changes.
        result["C"].extend(paragraph_chunks)
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temp_path.replace(path)


def _write_traces(path: Path, traces: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
        for trace in traces:
            stream.write(json.dumps(trace, ensure_ascii=False) + "\n")
    temp_path.replace(path)


def _write_manual_audit_template(
    output_path: Path,
    pages: list[DocumentPage],
    chunks_by_strategy: dict[str, list[Chunk]],
    traces: list[dict[str, Any]],
) -> None:
    """Prepare blank human labels; never infer coherence or grounding labels."""
    rows: list[dict[str, Any]] = []
    pages_by_document: dict[str, list[int]] = {}
    for page in pages:
        pages_by_document.setdefault(page.document_id, []).append(page.page)
    for page_numbers in pages_by_document.values():
        page_numbers.sort()
    sampled_pages: list[tuple[str, int]] = []
    sample_depth = 0
    document_ids = sorted(pages_by_document)
    while len(sampled_pages) < 10:
        added = False
        for document_id in document_ids:
            page_numbers = pages_by_document[document_id]
            if sample_depth < len(page_numbers):
                sampled_pages.append((document_id, page_numbers[sample_depth]))
                added = True
                if len(sampled_pages) == 10:
                    break
        if not added:
            break
        sample_depth += 1
    page_by_key = {(page.document_id, page.page): page for page in pages}
    for strategy, chunks in chunks_by_strategy.items():
        for document_id, page_number in sampled_pages:
            page = page_by_key[(document_id, page_number)]
            for chunk in chunks:
                if chunk.document_id == document_id and chunk.page == page_number:
                    rows.append({
                        "audit_type": "coherence",
                        "strategy": strategy,
                        "question_id": "",
                        "question": "",
                        "rank": "",
                        "document_id": document_id,
                        "source": chunk.source,
                        "page": page_number,
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "metadata_json": json.dumps(chunk.metadata, ensure_ascii=False),
                        "expected_filter": "",
                        "coherence_0_1_2": "",
                        "metadata_correct": "",
                        "filter_compliant": "",
                        "grounding_0_1_2": "",
                        "rationale": "",
                    })

    test_ids = [trace["id"] for trace in traces if trace["split"] == "test"]
    chosen_test_ids = set(test_ids[:5])
    for trace in traces:
        if trace["split"] != "test" or trace["id"] not in chosen_test_ids:
            continue
        for hit in trace["hits"][:3]:
            rows.append({
                "audit_type": "test_hit",
                "strategy": trace["strategy"],
                "question_id": trace["id"],
                "question": trace["question"],
                "rank": hit["rank"],
                "document_id": hit["document_id"],
                "source": hit["source"],
                "page": hit["page"],
                "chunk_id": hit["chunk_id"],
                "text": hit["text"],
                "metadata_json": json.dumps(hit["metadata"], ensure_ascii=False),
                "expected_filter": json.dumps(trace["applied_filter"], ensure_ascii=False),
                "coherence_0_1_2": "",
                "metadata_correct": "",
                "filter_compliant": "",
                "grounding_0_1_2": "",
                "rationale": "",
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "audit_type", "strategy", "question_id", "question", "rank", "document_id", "source", "page",
        "chunk_id", "text", "metadata_json", "expected_filter", "coherence_0_1_2", "metadata_correct",
        "filter_compliant", "grounding_0_1_2", "rationale",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 06 PDF ingestion and pgvector benchmark pipeline")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data" / "manifest.json")
    parser.add_argument("--questions", type=Path, default=REPO_ROOT / "benchmark" / "questions.json")
    parser.add_argument("--ingest-only", action="store_true", help="build and store A/B/C indexes without running benchmark")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv(ROOT / ".env")

    # Validate the benchmark before model loading or database writes on a full run.
    questions = None if args.ingest_only else _load_questions(args.questions.resolve())
    pages, corpus_stats = load_corpus(args.manifest.resolve())
    chunks_by_strategy = _make_strategy_chunks(pages)
    logger.info("Selected %d content pages: %s", corpus_stats["content_pages"], corpus_stats["pages_by_document"])

    embedder = MyEmbedder(os.getenv("EMBEDDING_MODEL") or None)
    database_url = os.getenv("DATABASE_URL", "")
    store = PgVectorStore(database_url, embedder.dimensions)
    store.create_schema()

    results_dir = ROOT / "results"
    run_info: dict[str, Any] = {
        "corpus": corpus_stats,
        "embedding_model": embedder.model_name,
        "embedding_dimensions": embedder.dimensions,
        "vector_store": "PostgreSQL + pgvector",
        "metric": "cosine distance",
        "strategies": {},
    }
    vectors_by_strategy: dict[str, list[list[float]]] = {}
    for strategy, chunks in chunks_by_strategy.items():
        start = time.perf_counter()
        if strategy == "C":
            vectors = vectors_by_strategy["B"]
            embedding_seconds = 0.0
            embedding_reused_from = "B"
        else:
            embedding_start = time.perf_counter()
            vectors = embedder.embed_documents([chunk.text for chunk in chunks])
            embedding_seconds = time.perf_counter() - embedding_start
            embedding_reused_from = None
        store_start = time.perf_counter()
        store.upsert(strategy, chunks, vectors)
        store_seconds = time.perf_counter() - store_start
        elapsed = time.perf_counter() - start
        vectors_by_strategy[strategy] = vectors
        lengths = [len(chunk.text) for chunk in chunks]
        run_info["strategies"][strategy] = {
            "chunk_count": len(chunks),
            "characters": sum(lengths),
            "chunk_length_min": min(lengths) if lengths else 0,
            "chunk_length_max": max(lengths) if lengths else 0,
            "embedding_seconds": round(embedding_seconds, 3),
            "store_seconds": round(store_seconds, 3),
            "wall_seconds": round(elapsed, 3),
            "embedding_reused_from": embedding_reused_from,
            "cost": 0,
        }
        logger.info("Indexed strategy %s: %d chunks in %.2fs", strategy, len(chunks), elapsed)

    _write_json(results_dir / "ingest_summary.json", run_info)
    if args.ingest_only:
        logger.info("Ingestion complete. Retrieval benchmark was not run (--ingest-only).")
        return

    assert questions is not None
    query_vectors: dict[str, list[float]] = {}
    traces: list[dict[str, Any]] = []
    for strategy in ("A", "B", "C"):
        for question in questions:
            query_id = str(question["id"])
            if query_id not in query_vectors:
                query_vectors[query_id] = embedder.embed_query(str(question["question"]))
            query_vector = query_vectors[query_id]
            filters = question.get("filter", {}) if strategy == "C" else {}
            hits = store.search(strategy, query_vector, top_k=3, filters=filters)
            trace = evaluate_query(question, hits)
            trace["strategy"] = strategy
            trace["applied_filter"] = filters
            traces.append(trace)

    summary = summarize(traces)
    run_info["manual_grounding_test_ids"] = list(dict.fromkeys(
        trace["id"] for trace in traces if trace["split"] == "test"
    ))[:5]
    _write_json(results_dir / "ingest_summary.json", run_info)
    _write_traces(results_dir / "traces.jsonl", traces)
    _write_json(results_dir / "retrieval_summary.json", summary)
    _write_manual_audit_template(results_dir / "manual_audit_template.csv", pages, chunks_by_strategy, traces)
    logger.info("Benchmark retrieval complete. Human coherence, metadata, and grounding labels remain blank for manual audit.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc)
        sys.exit(1)
