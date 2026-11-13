"""Record the chunk snapshot explicitly approved by the user at Gate 3."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    approvals = json.loads((ROOT / 'data/approvals.json').read_text(encoding='utf-8'))
    if approvals['human_gate_3']['status'] != 'approved':
        raise SystemExit('Gate 3 is not approved')
    path = ROOT / 'results/CHUNKS_LOCK.json'
    lock = json.loads((ROOT / 'benchmark/LOCK.json').read_text(encoding='utf-8'))
    payload = {'status': 'approved_before_retrieval', 'approved_on': '2026-11-13',
               'benchmark_sha256': lock['questions_sha256'],
               'chunk_hashes': {c: hashlib.sha256((ROOT / f'results/chunks_{c}.jsonl').read_bytes()).hexdigest()
                                for c in ['A', 'B', 'C']}}
    if path.exists() and json.loads(path.read_text(encoding='utf-8')) != payload:
        raise SystemExit('An approved chunk snapshot already exists and differs')
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(payload))


if __name__ == '__main__':
    main()
