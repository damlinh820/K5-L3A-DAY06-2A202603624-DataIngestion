"""Phase 1: inspect text PDFs and preserve source/page provenance (no OCR)."""
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]


def normalize(text):
    text = unicodedata.normalize('NFC', text).replace('\u00a0', ' ')
    lines = []
    for line in text.splitlines():
        line = re.sub(r'[ \t]+', ' ', line).strip()
        if re.search(r'CÔNG BÁO\s*/\s*Số', line, re.I) or re.fullmatch(r'\d+', line):
            continue
        if line:
            lines.append(line)
    # Retain line boundaries so chapter/article/clause markers can be recognized.
    return '\n'.join(lines)


def main():
    if (ROOT / 'benchmark/LOCK.json').exists():
        raise SystemExit('Corpus is locked before retrieval. Do not regenerate this snapshot; run verify_evidence.py instead.')
    results = ROOT / 'results'
    results.mkdir(exist_ok=True)
    approval_path = ROOT / 'data' / 'approvals.json'
    approvals = json.loads(approval_path.read_text(encoding='utf-8')) if approval_path.exists() else {}
    gate_status = approvals.get('human_gate_1', {}).get('status', 'pending')
    documents, pages, events = [], [], []
    for part in (1, 2, 3):
        path = ROOT / 'data' / f'luatdat{part}.pdf'
        records = []
        with pdfplumber.open(path) as pdf:
            physical = len(pdf.pages)
            for number, page in enumerate(pdf.pages, 1):
                try:
                    raw = page.extract_text(layout=False) or ''
                    text = normalize(raw)
                    error = None
                except Exception as exc:
                    raw, text, error = '', '', type(exc).__name__
                record = {'document_id': f'luatdat{part}', 'source_id': f'luatdat{part}',
                          'part': part, 'page': number, 'raw_text': raw, 'text': text,
                          'char_count': len(text), 'error': error}
                records.append(record)
                events.append({'source_id': record['source_id'], 'page': number,
                               'characters': len(text), 'status': 'error' if error else ('text' if text else 'empty'),
                               'error': error})
        counted = [r['page'] for r in records if r['text'] and not r['error']]
        documents.append({'source_id': f'luatdat{part}', 'document_id': f'luatdat{part}',
                          'title': f'Luật Đất đai số 31/2024/QH15 - phần {part}',
                          'law_number': '31/2024/QH15', 'part': part,
                          'local_path': f'data/luatdat{part}.pdf',
                          'source_path_or_url': f'https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_{part}.pdf',
                          'source_landing_page': 'https://chinhphu.vn/?pageid=27160&docid=211189&classid=1&typegroupid=3',
                          'source_status': 'User supplied official portal source; title and physical page counts match the three attachments; binary equality not yet checked',
                          'license_or_permission': 'Official law text from chinhphu.vn. Portal instructs attribution to www.chinhphu.vn or Cục Thông tin và Truyền thông Chính phủ when republishing its information. Corpus selection/count approval is recorded separately in data/approvals.json.',
                          'inspected_at': datetime.now(timezone.utc).isoformat(),
                          'accessed_at': '2026-11-13', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                          'pages_physical': physical, 'pages_counted': counted,
                          'page_rule': 'Physical PDF pages with extracted body text; remove repeated gazette header and number-only lines; exclude empty/error pages. Corpus selection approved via data/approvals.json; full manual per-page quality review is not claimed.',
                          'char_count': sum(r['char_count'] for r in records),
                          'normalization': 'NFC; normalize horizontal spaces; remove gazette header/number-only lines; preserve legal markers and line boundaries; do not guess corrections to words.'})
        pages.extend(records)
        print(f'{path.name}: {len(counted)}/{physical} pages with body text', flush=True)
    manifest = {'corpus_id': 'land-law-31-2024-original-gazette',
                'scope': 'Snapshot provided in three continuation PDFs; not a claim of current consolidated law',
                'human_gate_1': gate_status, 'total_pages_counted': sum(len(d['pages_counted']) for d in documents),
                'documents': documents}
    (ROOT / 'data' / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name, items in [('pages.jsonl', pages), ('extraction_log.jsonl', events)]:
        with (results / name).open('w', encoding='utf-8') as stream:
            for item in items:
                stream.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Total counted pages: {manifest['total_pages_counted']}; HUMAN GATE 1 {gate_status}")


if __name__ == '__main__':
    main()
