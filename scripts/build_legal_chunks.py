"""Export legal A/B/C chunks and pre-embedding statistics, without retrieval."""
import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunkers import fixed, heading, hybrid
from src.extract import load_corpus


def main():
    if (ROOT / 'results/CHUNKS_LOCK.json').exists():
        raise SystemExit('Chunks are approved and locked; do not rebuild this experiment snapshot.')
    text, spans = load_corpus()
    result = ROOT / 'results'
    rows = []
    for name, builder in [('A', fixed), ('B', heading), ('C', hybrid)]:
        chunks = builder(text, spans)
        target = result / f'chunks_{name}.jsonl'
        with target.open('w', encoding='utf-8', newline='\n') as stream:
            for chunk in chunks:
                stream.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        tokens = [c['n_tokens'] for c in chunks]
        row = {'config': name, 'chunk_count': len(chunks),
               'tokens_min': min(tokens), 'tokens_median': statistics.median(tokens),
               'tokens_max': max(tokens), 'tokens_total': sum(tokens),
               'articles': len({c['article'] for c in chunks if c['article'] is not None}),
               'chunks_over_8192': sum(t > 8192 for t in tokens),
               'chunk_file_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
        rows.append(row)
        print(json.dumps(row), flush=True)
    with (result / 'chunk_stats.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
