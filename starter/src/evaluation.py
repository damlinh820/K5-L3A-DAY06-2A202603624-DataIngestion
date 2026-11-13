"""Retrieval evidence metrics and machine-readable per-query traces."""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Any


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFC", value or "").casefold()
    return re.sub(r"\s+", " ", value).strip()


def _gold_evidence(question: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = question.get("gold_evidence")
    if evidence:
        return evidence if isinstance(evidence, list) else [evidence]
    required = ("gold_source_id", "gold_page", "evidence_quote")
    missing = [key for key in required if question.get(key) in (None, "")]
    if missing:
        raise ValueError(f"Question {question.get('id', '?')} missing gold fields: {', '.join(missing)}")
    return [{
        "source_id": question["gold_source_id"],
        "page": question["gold_page"],
        "evidence_quote": question["evidence_quote"],
    }]


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate evidence retrieval only; human grounding/coherence remain manual."""
    gold = _gold_evidence(question)
    hit_details = []
    for rank, hit in enumerate(hits, start=1):
        matching_gold = []
        for item in gold:
            source_match = (
                hit.get("document_id") == item.get("source_id")
                or hit.get("source") == item.get("source")
            )
            page_match = hit.get("page") == item.get("page")
            quote = _norm(item.get("evidence_quote", ""))
            text = _norm(hit.get("text", ""))
            evidence_match = bool(quote) and quote in text
            if source_match and page_match and evidence_match:
                matching_gold.append(item)
        hit_details.append({
            **hit,
            "rank": rank,
            "evidence_hit": bool(matching_gold),
            "matched_gold": matching_gold,
        })

    return {
        "id": question.get("id"),
        "split": question.get("split"),
        "question": question.get("question"),
        "expected_answer": question.get("expected_answer"),
        "gold_evidence": gold,
        "filter": question.get("filter") or {},
        "hits": hit_details,
        "hit_at_1": bool(hit_details and hit_details[0]["evidence_hit"]),
        "evidence_hit_at_3": any(hit["evidence_hit"] for hit in hit_details[:3]),
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate retrieval metrics by strategy and benchmark split."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for trace in traces:
        groups[(trace["strategy"], trace["split"])].append(trace)

    summary: dict[str, Any] = {}
    for (strategy, split), rows in sorted(groups.items()):
        total = len(rows)
        hit1 = sum(bool(row["hit_at_1"]) for row in rows)
        hit3 = sum(bool(row["evidence_hit_at_3"]) for row in rows)
        summary.setdefault(strategy, {})[split] = {
            "questions": total,
            "hit_at_1": {"count": hit1, "total": total, "rate": hit1 / total if total else None},
            "evidence_hit_at_3": {"count": hit3, "total": total, "rate": hit3 / total if total else None},
        }
    return summary
