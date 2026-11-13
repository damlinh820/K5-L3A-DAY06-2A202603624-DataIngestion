"""Independently reopen persistent indexes and verify ingestion artifacts; no queries."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extract import validate_lock
from src.store import LegalStore, metadata


def main():
    validate_lock()
    store = LegalStore('openai/text-embedding-3-small')
    approvals = json.loads((ROOT / 'data/approvals.json').read_text(encoding='utf-8'))
    summary = {'status': 'passed', 'retrieval_run': (ROOT / 'results/trace_A_dev.jsonl').exists(),
               'gate_3': approvals['human_gate_3']['status'], 'configs': {}}
    for name in ['A', 'B', 'C']:
        path = ROOT / f'results/chunks_{name}.jsonl'
        chunks = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        ingest = json.loads((ROOT / f'results/ingest_{name}.json').read_text(encoding='utf-8'))
        if ingest['status'] != 'complete' or hashlib.sha256(path.read_bytes()).hexdigest() != ingest['chunk_file_sha256']:
            raise ValueError(f'{name}: chunks differ from completed ingestion')
        coll = store.collection(name)
        actual = coll.get(include=['documents', 'metadatas'])
        persisted = {key: (text, meta) for key, text, meta in zip(actual['ids'], actual['documents'], actual['metadatas'])}
        assert len(persisted) == len(chunks) == ingest['repeat_write']['count']
        for chunk in chunks:
            text, meta = persisted[chunk['chunk_id']]
            assert text == chunk['text'] and meta == metadata(chunk)
        vector = coll.get(ids=[chunks[0]['chunk_id']], include=['embeddings'])['embeddings'][0]
        assert len(vector) == 1536
        summary['configs'][name] = {'count': len(chunks), 'repeated_count': ingest['repeat_write']['count'],
                                   'all_persisted_text_metadata_match': True,
                                   'embedding_dimension_sample': len(vector),
                                   'embedding': ingest['embedding'],
                                   'wall_seconds_including_repeat': ingest['wall_seconds_including_repeat']}
    with (ROOT / 'results/chunk_stats.csv').open(encoding='utf-8', newline='') as stream:
        summary['chunk_stats'] = list(csv.DictReader(stream))
    summary['ingest_api_tokens_actual'] = sum(c['embedding']['actual_api_tokens'] for c in summary['configs'].values())
    summary['ingest_api_cost_usd_actual'] = round(sum(c['embedding']['actual_api_cost_usd'] for c in summary['configs'].values()), 10)
    summary['wall_seconds_including_repeat'] = sum(c['wall_seconds_including_repeat'] for c in summary['configs'].values())
    summary['benchmark_lock_commit'] = subprocess.run(['git', 'rev-parse', '65922c5'], cwd=ROOT,
                                                     capture_output=True, text=True, check=True).stdout.strip()
    summary['notes'] = ['A/B/C share the same real model and embedding cache; timing is not a cold-cache comparison.',
                        'Persisted text/metadata match checks are automated ingestion checks, not independent source audit labels.',
                        'This index consistency check runs no retrieval queries and generates no manual audit labels.']
    (ROOT / 'results/phase3_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key not in {'configs', 'chunk_stats'}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
