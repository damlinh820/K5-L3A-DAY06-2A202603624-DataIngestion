"""Load the approved extracted page snapshot and build source-offset provenance."""
import hashlib
import json
from pathlib import Path

from .normalize import normalize

ROOT = Path(__file__).resolve().parents[1]


def matches_snapshot(data, expected):
    # Git on Windows may change only line endings when checking out text files.
    lf = data.replace(b'\r\n', b'\n')
    return expected in {hashlib.sha256(candidate).hexdigest()
                        for candidate in (data, lf, lf.replace(b'\n', b'\r\n'))}


def validate_lock():
    lock = json.loads((ROOT / 'benchmark/LOCK.json').read_text(encoding='utf-8'))
    for relative, key in [('benchmark/questions.jsonl', 'questions_sha256'),
                          ('benchmark/protocol.json', 'protocol_sha256'),
                          ('results/pages.jsonl', 'pages_sha256'), ('data/manifest.json', 'manifest_sha256')]:
        if not matches_snapshot((ROOT / relative).read_bytes(), lock[key]):
            raise RuntimeError(f'Locked file changed: {relative}; stop before ingestion/retrieval')
    return lock


def load_corpus():
    validate_lock()
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    sources = {d['source_id']: d for d in manifest['documents']}
    pages = [json.loads(line) for line in (ROOT / 'results/pages.jsonl').read_text(encoding='utf-8').splitlines()]
    text, spans = '', []
    for p in pages:
        if p['page'] not in sources[p['source_id']]['pages_counted']:
            continue
        clean = normalize(p['text'])
        if not clean or p.get('error'):
            raise ValueError(f"Invalid counted page: {p['source_id']}:{p['page']}")
        start = len(text)
        text += clean + '\n'
        spans.append({'start': start, 'end': len(text), 'document_id': p['source_id'],
                      'page': p['page'], 'part': p['part'],
                      'source': sources[p['source_id']]['source_path_or_url']})
    return text, spans


def provenance(spans, start, end):
    return [{**s, 'start': max(start, s['start']), 'end': min(end, s['end'])}
            for s in spans if s['end'] > start and s['start'] < end]
