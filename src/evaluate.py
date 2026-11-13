"""Locked dev/test evidence evaluation; no generated human audit labels."""
import argparse
import csv
import hashlib
import json
import logging
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from .embed import OpenRouterEmbedder
from .extract import load_corpus, validate_lock
from .retrieve import retrieve
from .store import LegalStore

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
LOG = logging.getLogger(__name__)


def fold(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    temp.replace(path)


def write_jsonl(path, rows):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    temp.replace(path)


def code_snapshot():
    names = ['chunkers', 'normalize', 'tokenizer', 'embed', 'store', 'retrieve', 'evaluate', 'extract']
    return {f'src/{name}.py': sha(ROOT / f'src/{name}.py') for name in names}


def quote_in_source_intervals(corpus, quote, intervals, source_id, page):
    intervals = sorted((p['start'], p['end']) for p in intervals
                       if p['document_id'] == source_id and p['page'] == page)
    merged = []
    for start, end in intervals:
        if merged and (start <= merged[-1][1] or not corpus[merged[-1][1]:start].strip()):
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return bool(quote) and any(fold(quote) in fold(corpus[start:end]) for start, end in merged)


def evidence_checks(corpus, hit, golds):
    proofs = []
    intervals = hit['provenance'] + hit.get('context_provenance', [])
    for gold in golds:
        text_match = bool(gold['evidence_quote']) and fold(gold['evidence_quote']) in fold(hit['text'])
        page_match = any(p['document_id'] == gold['source_id'] and p['page'] == gold['page'] for p in intervals)
        quote_on_gold_page = quote_in_source_intervals(corpus, gold['evidence_quote'], intervals,
                                                       gold['source_id'], gold['page'])
        proofs.append({'gold_source_id': gold['source_id'], 'gold_page': gold['page'],
                       'quote_in_text': text_match, 'has_gold_page': page_match,
                       'quote_from_gold_page': quote_on_gold_page,
                       'hit': bool(text_match and page_match and quote_on_gold_page)})
    return proofs


def evaluate_hits(corpus, question, hits, config, variant='base', applied_filter=None):
    golds = question['gold_evidence']
    scored = []
    for hit in hits:
        checks = evidence_checks(corpus, hit, golds)
        scored.append({**hit, 'evidence_hit': any(p['hit'] for p in checks), 'evidence_checks': checks})
    hit1 = bool(scored and scored[0]['evidence_hit'])
    hit3 = any(hit['evidence_hit'] for hit in scored[:3])
    all_intervals = [p for hit in scored[:3] for p in hit['provenance'] + hit.get('context_provenance', [])]
    union_covered = any(quote_in_source_intervals(corpus, g['evidence_quote'], all_intervals,
                                                  g['source_id'], g['page']) for g in golds)
    requested_filter = question.get('filter', {})
    compliance = (bool(scored) and all(all(hit['metadata'].get(k) == v for k, v in requested_filter.items())
                                     for hit in scored[:3])) if requested_filter else None
    return {'id': question['id'], 'split': question['split'], 'config': config, 'variant': variant,
            'question': question['question'], 'expected_answer': question['expected_answer'],
            'gold_evidence': golds, 'requested_filter': requested_filter, 'applied_filter': applied_filter or {},
            'hits': scored, 'hit_at_1': hit1, 'evidence_hit_at_3': hit3,
            'evidence_split_across_top3': bool(union_covered and not hit3),
            'requested_scope_satisfied_by_all_top3': compliance}


def metrics_for(rows, name, split):
    n = len(rows)
    one = sum(row['hit_at_1'] for row in rows)
    three = sum(row['evidence_hit_at_3'] for row in rows)
    return {'strategy': name, 'split': split, 'questions': n,
            'hit_at_1_count': one, 'hit_at_1_total': n, 'hit_at_1_rate': one / n if n else None,
            'evidence_hit_at_3_count': three, 'evidence_hit_at_3_total': n,
            'evidence_hit_at_3_rate': three / n if n else None}


def choose_config(dev_metrics, document_tokens):
    if any(row['split'] != 'dev' for row in dev_metrics):
        raise ValueError('Selection may only use dev metrics')
    if {row['strategy'] for row in dev_metrics} != {'A', 'B', 'C'}:
        raise ValueError('Selection requires exactly the three base configs')
    ranked = sorted(dev_metrics, key=lambda row: (-row['evidence_hit_at_3_rate'], -row['hit_at_1_rate'],
                                                 document_tokens[row['strategy']], row['strategy']))
    return ranked[0]['strategy'], ranked


def validate_indexes(store, approved):
    lookups = {}
    for config in ['A', 'B', 'C']:
        path = RESULTS / f'chunks_{config}.jsonl'
        status = read_json(RESULTS / f'ingest_{config}.json')
        if (status['status'] != 'complete' or sha(path) != approved['chunk_hashes'][config]
                or sha(path) != status['chunk_file_sha256']):
            raise RuntimeError(f'Unapproved/incomplete chunk snapshot: {config}')
        chunks = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        coll = store.collection(config)
        actual = coll.get(include=[])
        if set(actual['ids']) != {c['chunk_id'] for c in chunks}:
            raise RuntimeError(f'Index ID snapshot mismatch: {config}')
        lookups[config] = {c['chunk_id']: c for c in chunks}
    return lookups


def refresh_metrics():
    rows = []
    for split in ['dev', 'test']:
        for name in ['A', 'B', 'C', 'B_filter', 'B_filter_baseline']:
            path = RESULTS / f'trace_{name}_{split}.jsonl'
            if path.exists():
                traces = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
                rows.append(metrics_for(traces, name, split))
    if rows:
        with (RESULTS / 'metrics.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    for name in ['A', 'B', 'C', 'B_filter', 'B_filter_baseline']:
        combined = []
        for split in ['dev', 'test']:
            path = RESULTS / f'trace_{name}_{split}.jsonl'
            if path.exists():
                combined.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines())
        if combined:
            write_jsonl(RESULTS / f'trace_{name}.jsonl', combined)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--split', required=True, choices=['dev', 'test'])
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler(RESULTS / 'retrieval_log.txt', encoding='utf-8')])
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    lock = validate_lock()
    approvals = read_json(ROOT / 'data/approvals.json')
    if approvals['human_gate_3']['status'] != 'approved':
        raise RuntimeError('Human Gate 3 must be approved before corpus retrieval')
    approved = read_json(RESULTS / 'CHUNKS_LOCK.json')
    if approved['benchmark_sha256'] != lock['questions_sha256']:
        raise RuntimeError('Gate 3 approved a different benchmark snapshot')
    selection_path = RESULTS / 'dev_selection.json'
    if args.split == 'dev' and ((RESULTS / 'test_run.json').exists() or selection_path.exists()):
        raise RuntimeError('Dev selection already frozen or test started; no automatic retuning/rerun')
    if args.split == 'test':
        if not selection_path.exists():
            raise RuntimeError('Select and freeze the dev configuration before test')
        selection = read_json(selection_path)
        if (selection['code_snapshot'] != code_snapshot() or selection['chunk_hashes'] != approved['chunk_hashes']
                or selection['benchmark_sha256'] != lock['questions_sha256']):
            raise RuntimeError('Model/code/chunk/benchmark configuration changed after dev selection')
        for config in ['A', 'B', 'C']:
            if sha(RESULTS / f'trace_{config}_dev.jsonl') != selection['dev_trace_hashes'][config]:
                raise RuntimeError('Frozen dev trace changed')
        if (RESULTS / 'test_run.json').exists():
            raise RuntimeError('Test run already recorded; do not rerun to search for better scores')
    protocol = read_json(ROOT / 'benchmark/protocol.json')
    questions = [json.loads(line) for line in (ROOT / 'benchmark/questions.jsonl').read_text(encoding='utf-8').splitlines()]
    questions = [q for q in questions if q['split'] == args.split]
    expected_ids = lock[f'{args.split}_ids']
    if [q['id'] for q in questions] != expected_ids:
        raise RuntimeError('Question split differs from locked IDs')
    store = LegalStore(protocol['model'])
    lookups = validate_indexes(store, approved)
    corpus, _ = load_corpus()
    started = time.perf_counter()
    embedder = OpenRouterEmbedder(protocol['model'], protocol['dimensions'])
    try:
        vectors, usage = embedder.embed([q['question'] for q in questions], f'retrieval_{args.split}_queries')
    finally:
        embedder.close()
    base_traces, metrics = {}, []
    for config in ['A', 'B', 'C']:
        traces = []
        for question, vector in zip(questions, vectors):
            # No gold/answer/source is passed into retrieve(), only vector + index config.
            hits = retrieve(store, config, vector, lookups[config])
            trace = evaluate_hits(corpus, question, hits, config)
            traces.append(trace)
            LOG.info('%s/%s %s Hit@1=%s EvidenceHit@3=%s', args.split, config,
                     question['id'], trace['hit_at_1'], trace['evidence_hit_at_3'])
        base_traces[config] = traces
        write_jsonl(RESULTS / f'trace_{config}_{args.split}.jsonl', traces)
        metrics.append(metrics_for(traces, config, args.split))
    filtered, baseline = [], []
    for question, vector in zip(questions, vectors):
        if not question['filter']:
            continue
        hits = retrieve(store, 'B', vector, lookups['B'], user_filter=question['filter'])
        filtered.append(evaluate_hits(corpus, question, hits, 'B', variant='metadata_filter', applied_filter=question['filter']))
        baseline.append(next(row for row in base_traces['B'] if row['id'] == question['id']))
    write_jsonl(RESULTS / f'trace_B_filter_{args.split}.jsonl', filtered)
    write_jsonl(RESULTS / f'trace_B_filter_baseline_{args.split}.jsonl', baseline)
    write_json(RESULTS / f'retrieval_usage_{args.split}.json', {'split': args.split, 'query_embedding': usage,
        'retrieval_wall_seconds_including_cache_load': time.perf_counter() - started,
        'questions_embedded_once_and_shared_across_configs': True})
    refresh_metrics()
    if args.split == 'dev':
        with (RESULTS / 'chunk_stats.csv').open(encoding='utf-8', newline='') as stream:
            counts = {row['config']: int(row['tokens_total']) for row in csv.DictReader(stream)}
        selected, ranked = choose_config(metrics, counts)
        write_json(selection_path, {'status': 'frozen_before_test', 'selected_config': selected,
            'at_utc': datetime.now(timezone.utc).isoformat(), 'criteria': protocol['selection_rule'],
            'ranked_dev_metrics': ranked, 'document_embedding_tokens': counts,
            'benchmark_sha256': lock['questions_sha256'], 'chunk_hashes': approved['chunk_hashes'],
            'code_snapshot': code_snapshot(),
            'dev_trace_hashes': {c: sha(RESULTS / f'trace_{c}_dev.jsonl') for c in ['A', 'B', 'C']},
            'test_retrieval_has_run': False})
        LOG.info('Dev selection frozen before test: %s', selected)
    else:
        write_json(RESULTS / 'test_run.json', {'status': 'complete', 'at_utc': datetime.now(timezone.utc).isoformat(),
            'selected_config_frozen_before_test': selection['selected_config'],
            'selection_file_sha256': sha(selection_path), 'benchmark_sha256': lock['questions_sha256'],
            'test_ids': expected_ids, 'test_metrics_used_for_tuning': False})
    print(json.dumps(metrics))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        LOG.exception('Retrieval evaluation stopped without fallback')
        raise
