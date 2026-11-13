"""Batch-embed and persist A/B/C; no benchmark retrieval before HUMAN GATE 3."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from .embed import OpenRouterEmbedder
from .extract import validate_lock
from .store import LegalStore

ROOT = Path(__file__).resolve().parents[1]
LOG = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', choices=['A', 'B', 'C', 'all'], required=True)
    parser.add_argument('--verify-reingest', action='store_true')
    args = parser.parse_args()
    lock = validate_lock()
    approvals = json.loads((ROOT / 'data/approvals.json').read_text(encoding='utf-8'))
    if approvals['human_gate_2']['status'] != 'approved':
        raise RuntimeError('Gate 2 is not approved')
    if approvals['human_gate_3']['status'] == 'approved':
        raise RuntimeError('Indexes already approved at Gate 3; do not replace the frozen experiment snapshot')
    result_dir = ROOT / 'results'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler(result_dir / 'ingest_log.txt', encoding='utf-8')])
    # Avoid httpx request logging; only sanitized purpose/status/usage is recorded.
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    protocol = json.loads((ROOT / 'benchmark/protocol.json').read_text(encoding='utf-8'))
    model = protocol['model']
    embedder = OpenRouterEmbedder(model, protocol['dimensions'])
    store = LegalStore(model)
    configs = ['A', 'B', 'C'] if args.config == 'all' else [args.config]
    try:
        for config in configs:
            start = time.perf_counter()
            path = result_dir / f'chunks_{config}.jsonl'
            chunks = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
            status = {'status': 'in_progress', 'config': config, 'model': model,
                      'dimensions': protocol['dimensions'], 'metric': 'cosine',
                      'search': 'Chroma HNSW approximate cosine; no custom index tuning',
                      'chroma_version': importlib.metadata.version('chromadb'),
                      'at_utc': datetime.now(timezone.utc).isoformat(),
                      'benchmark_sha256': lock['questions_sha256'],
                      'chunk_file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            output = result_dir / f'ingest_{config}.json'
            output.write_text(json.dumps(status, indent=2), encoding='utf-8')
            vectors, usage = embedder.embed([c['text'] for c in chunks], f'ingest_{config}')
            storage_start = time.perf_counter()
            first = store.replace(config, chunks, vectors)
            storage_seconds = time.perf_counter() - storage_start
            again = None
            repeat_seconds = None
            if args.verify_reingest:
                repeat_start = time.perf_counter()
                again = store.replace(config, chunks, vectors)
                repeat_seconds = time.perf_counter() - repeat_start
                if first['count'] != again['count'] or again['obsolete_removed']:
                    raise RuntimeError('Idempotent re-ingestion check failed')
            status.update({'status': 'complete', 'chunks': len(chunks), 'embedding': usage,
                           'first_write': first, 'repeat_write': again,
                           'store_seconds': storage_seconds, 'repeat_store_seconds': repeat_seconds,
                           'wall_seconds_including_repeat': time.perf_counter() - start})
            output.write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
            with (result_dir / 'ingest_history.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(status) + '\n')
            LOG.info('COMPLETE %s: %d persisted chunks; repeat=%s; usage=%s', config, len(chunks), again, usage)
    finally:
        embedder.close()
    stats_path = result_dir / 'chunk_stats.csv'
    with stats_path.open(encoding='utf-8', newline='') as stream:
        stats = list(csv.DictReader(stream))
    for row in stats:
        path = result_dir / f"ingest_{row['config']}.json"
        if path.exists():
            status = json.loads(path.read_text(encoding='utf-8'))
            if status['status'] == 'complete':
                row.update({'embedding_seconds': status['embedding']['seconds'],
                            'store_seconds': status['store_seconds'],
                            'repeat_store_seconds': status['repeat_store_seconds'],
                            'api_tokens_actual': status['embedding']['actual_api_tokens'],
                            'api_cost_usd_actual': status['embedding']['actual_api_cost_usd'],
                            'repeat_count': status['repeat_write']['count'] if status['repeat_write'] else ''})
    fields = list(dict.fromkeys(key for row in stats for key in row))
    with stats_path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(stats)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        LOG.exception('Ingestion stopped; no fallback was used')
        raise
