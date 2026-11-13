# Phase 1 - dossier for HUMAN GATE 1

Corpus: three continuation PDFs of the same law, 31/2024/QH15, not three independent laws.
Source supplied by the student: https://chinhphu.vn/?pageid=27160&docid=211189&classid=1&typegroupid=3
The official portal lists all three attachments with matching page counts. Binary identity has not been checked.

| Source | Physical pages | Pages with extracted body text | Excluded |
|---|---:|---:|---|
| luatdat1 | 94 | 93 | physical page 94, empty |
| luatdat2 | 95 | 94 | physical page 95, empty |
| luatdat3 | 66 | 66 | none |
| Total | 255 | 253 | 2 empty pages |

Extraction: pdfplumber 0.11.9; no OCR. `results/pages.jsonl` preserves raw text and normalized text with source/page provenance. `results/extraction_log.jsonl` records every physical page. NFC, horizontal-space cleanup, gazette-header removal, and number-only line removal are applied; legal marker lines are preserved. No guessed repairs of broken Vietnamese words.

The portal requests source attribution when its information is republished. The manifest records this instruction and the source URLs. The student confirmed corpus selection/count at Gate 1 on 2026-11-13; evidence of approval is recorded in `data/approvals.json`. This does not claim manual review of every page. This corpus is the supplied historical publication, not a verified current consolidated version.

OpenRouter live model catalog was queried and one real Vietnamese sentence was embedded successfully:
- Requested model: `openai/text-embedding-3-small`; response model: `text-embedding-3-small`.
- Dimensions: 1536.
- Catalog input price: USD 0.00000002/token (USD 0.02/million tokens).
- Probe usage: 21 tokens; actual reported cost: USD 0.00000042.
- Evidence: `results/embedding_probe.json`; no key or vector is saved in that file.

Environment status:
- Old `starter/.venv` cannot start because its original Python installation is missing. It was preserved.
- A fresh `.venv-legal` was created with Python 3.12.14. Installed versions are pinned in `requirements.txt`; the complete dependency snapshot is in `requirements.lock.txt` and `results/environment.json`.
- Docker was not found in PATH or the standard installation path. Chroma 1.5.9 PersistentClient was selected as permitted by the plan, with cosine distance.
- `results/store_probe.json` records actual successful writes, repeat upsert (2 records remain 2), read/search in a separate process after reopening, and metadata filtering. It uses two isolated setup sentences with real OpenRouter vectors, not corpus/test questions. The extra probe used 37 tokens at a reported cost of USD 0.00000074.

Gate 1: approved. Gate 2 has also been confirmed; the benchmark snapshot was locked and committed as `65922c5` before retrieval. A/B/C were ingested with real vectors (see `phase3_summary.json`), and Gate 3 chunk review has been confirmed. Dev evaluation selected C before test; test evaluation is complete (see `dev_selection.json`, `test_run.json`, and `metrics.csv`). At Gate 4 the user subsequently requested assistant grading. All 30/45/15 audit rows now have disclosed AI-assisted labels, not independent human judgments; student verification is not claimed. See `AUDIT_REVIEW.md` and `audit_method.json`.
