"""Reproduce the locked corpus experiment in a new directory under runs/."""
import argparse
import csv
import json
import logging
import os
import shutil
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from . import embed as embedding_module
from .chunkers import fixed, heading, hybrid
from .evaluate import code_snapshot, evaluate_hits, metrics_for, choose_config
from .extract import load_corpus
from .retrieve import retrieve
from .store import LegalStore

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def write_jsonl(path, rows):
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New directory under runs/, e.g. runs/run01')
    parser.add_argument('--prepare-only', action='store_true', help='Build chunks without API calls')
    parser.add_argument('--reuse-cache', type=Path, help='Optional existing cache of real API responses')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT / 'runs') or output == ROOT / 'runs':
        parser.error('--output must be a new subdirectory under runs/')
    if output.exists():
        parser.error('Output already exists; choose a new directory, never overwrite an experiment')
    if args.reuse_cache and not args.reuse_cache.is_file():
        parser.error('--reuse-cache file does not exist')
    load_dotenv(ROOT / '.env')
    load_dotenv(ROOT / 'starter/.env')  # Existing local key; old starter code is not used.
    if not args.prepare_only and not os.getenv('OPENROUTER_API_KEY'):
        parser.error('Set OPENROUTER_API_KEY in .env before calling the real embedding API')
    corpus, spans = load_corpus()
    protocol = json.loads((ROOT / 'benchmark/protocol.json').read_text(encoding='utf-8'))
    questions = [json.loads(line) for line in (ROOT / 'benchmark/questions.jsonl').read_text(encoding='utf-8').splitlines()]
    output.mkdir(parents=True)
    result = output / 'results'
    result.mkdir()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler(output / 'run.log', encoding='utf-8')])
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    chunks = {'A': fixed(corpus, spans), 'B': heading(corpus, spans), 'C': hybrid(corpus, spans)}
    stats = []
    for config, rows in chunks.items():
        write_jsonl(result / f'chunks_{config}.jsonl', rows)
        sizes = [row['n_tokens'] for row in rows]
        stats.append({'config': config, 'chunks': len(rows), 'min_tokens': min(sizes),
                      'median_tokens': statistics.median(sizes), 'max_tokens': max(sizes),
                      'total_tokens': sum(sizes)})
    write_csv(result / 'chunk_stats.csv', stats)
    write_json(output / 'run.json', {'status': 'prepared', 'baseline': 'results/ in repository is unchanged',
                                    'model': protocol['model'], 'code_snapshot': code_snapshot(),
                                    'prepare_only': args.prepare_only, 'cache_reused': bool(args.reuse_cache)})
    if args.prepare_only:
        print(json.dumps({'status': 'prepared', 'output': str(output), 'chunks': {k: len(v) for k, v in chunks.items()}}))
        return
    if args.reuse_cache:
        shutil.copyfile(args.reuse_cache, result / 'embedding_cache.jsonl')
    # The frozen adapter uses ROOT for its cache/usage paths. Redirect that module
    # only, for this CLI process, so no original ledger or index can be changed.
    original_embedding_root = embedding_module.ROOT
    embedding_module.ROOT = output
    embedder = None
    try:
        embedder = embedding_module.OpenRouterEmbedder(protocol['model'], protocol['dimensions'])
        store = LegalStore(protocol['model'], path=result / 'chroma')
        lookups = {config: {c['chunk_id']: c for c in rows} for config, rows in chunks.items()}
        for config, rows in chunks.items():
            start = time.perf_counter()
            vectors, usage = embedder.embed([c['text'] for c in rows], f'ingest_{config}')
            first = store.replace(config, rows, vectors)
            repeat = store.replace(config, rows, vectors)
            if first['count'] != repeat['count'] or repeat['obsolete_removed']:
                raise RuntimeError('Repeated upsert changed the collection')
            write_json(result / f'ingest_{config}.json', {'config': config, 'embedding': usage,
                       'first_write': first, 'repeat_write': repeat, 'seconds': time.perf_counter() - start})
        traces = {name: [] for name in ['A', 'B', 'C', 'B_filter']}
        metrics = []
        selection = None
        for split in ['dev', 'test']:
            subset = [q for q in questions if q['split'] == split]
            vectors, usage = embedder.embed([q['question'] for q in subset], f'queries_{split}')
            write_json(result / f'query_usage_{split}.json', usage)
            for config in ['A', 'B', 'C']:
                for question, vector in zip(subset, vectors):
                    hits = retrieve(store, config, vector, lookups[config])
                    traces[config].append(evaluate_hits(corpus, question, hits, config, 'base', {}))
                metrics.append(metrics_for([t for t in traces[config] if t['split'] == split], config, split))
            if split == 'dev':
                selection, ranked = choose_config(metrics, {s['config']: s['total_tokens'] for s in stats})
                write_json(result / 'dev_selection.json', {'selected_config': selection,
                    'at_utc': datetime.now(timezone.utc).isoformat(), 'ranked_dev_metrics': ranked,
                    'criteria': protocol['selection_rule'], 'code_snapshot': code_snapshot()})
            for question, vector in zip(subset, vectors):
                if question.get('filter'):
                    hits = retrieve(store, 'B', vector, lookups['B'], question['filter'])
                    traces['B_filter'].append(evaluate_hits(corpus, question, hits, 'B', 'filtered', question['filter']))
            metrics.append(metrics_for([t for t in traces['B_filter'] if t['split'] == split], 'B_filter', split))
            baseline = [t for t in traces['B'] if t['split'] == split and t['requested_filter']]
            metrics.append(metrics_for(baseline, 'B_filter_baseline', split))
            for name, rows in traces.items():
                write_jsonl(result / f'trace_{name}.jsonl', rows)
            write_csv(result / 'metrics.csv', metrics)
        write_json(output / 'run.json', {'status': 'complete', 'model': protocol['model'],
            'selected_config': selection, 'at_utc': datetime.now(timezone.utc).isoformat(),
            'code_snapshot': code_snapshot(), 'cache_reused': bool(args.reuse_cache),
            'baseline': 'Original results/ unchanged; this is a reproduction, not a new independent holdout.',
            'audit': 'Existing AI-assisted audit labels were not regenerated.'})
        print(json.dumps({'status': 'complete', 'selected_config': selection, 'output': str(output)}))
    finally:
        if embedder is not None:
            embedder.close()
        embedding_module.ROOT = original_embedding_root


if __name__ == '__main__':
    main()
