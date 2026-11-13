"""Recompute evidence/metric consistency from saved traces without querying the index."""
import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.evaluate import code_snapshot, evaluate_hits, metrics_for, sha
from src.extract import load_corpus, validate_lock


def main():
    validate_lock()
    corpus, _ = load_corpus()
    questions = {q['id']: q for q in (json.loads(line) for line in (ROOT / 'benchmark/questions.jsonl').read_text(encoding='utf-8').splitlines())}
    result = ROOT / 'results'
    selection = json.loads((result / 'dev_selection.json').read_text(encoding='utf-8'))
    test_run = json.loads((result / 'test_run.json').read_text(encoding='utf-8'))
    assert selection['code_snapshot'] == code_snapshot()
    assert test_run['selection_file_sha256'] == sha(result / 'dev_selection.json')
    assert datetime.fromisoformat(selection['at_utc']) < datetime.fromisoformat(test_run['at_utc'])
    expected = {}
    query_checks, hit_checks = 0, 0
    for name in ['A', 'B', 'C', 'B_filter', 'B_filter_baseline']:
        rows = [json.loads(line) for line in (result / f'trace_{name}.jsonl').read_text(encoding='utf-8').splitlines()]
        assert len(rows) == (20 if name in {'A', 'B', 'C'} else 3)
        assert len({row['id'] for row in rows}) == len(rows)
        for row in rows:
            q = questions[row['id']]
            assert row['split'] == q['split'] and row['question'] == q['question']
            assert row['applied_filter'] == (q['filter'] if name == 'B_filter' else {})
            checked = evaluate_hits(corpus, q, row['hits'], row['config'], row['variant'], row['applied_filter'])
            assert checked['hit_at_1'] == row['hit_at_1']
            assert checked['evidence_hit_at_3'] == row['evidence_hit_at_3']
            assert checked['evidence_split_across_top3'] == row['evidence_split_across_top3']
            for hit in row['hits']:
                assert math.isfinite(hit['score']) and abs(hit['score'] - (1 - hit['cosine_distance'])) < 1e-9
                hit_checks += 1
            if name != 'B_filter_baseline':
                query_checks += 1
        for split in ['dev', 'test']:
            expected[(name, split)] = metrics_for([row for row in rows if row['split'] == split], name, split)
    with (result / 'metrics.csv').open(encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream):
            computed = expected[(row['strategy'], row['split'])]
            for field in ['questions', 'hit_at_1_count', 'hit_at_1_total', 'evidence_hit_at_3_count', 'evidence_hit_at_3_total']:
                assert int(row[field]) == computed[field]
            for field in ['hit_at_1_rate', 'evidence_hit_at_3_rate']:
                assert abs(float(row[field]) - computed[field]) < 1e-12
    usage = [json.loads(line) for line in (result / 'embedding_usage.jsonl').read_text(encoding='utf-8').splitlines()]
    total_tokens = sum(row['usage']['total_tokens'] for row in usage)
    total_cost = sum(row['usage']['cost'] for row in usage)
    report = {'status': 'passed', 'unique_query_variant_checks': query_checks,
              'hit_records_checked_including_filter_baselines': hit_checks,
              'selection_frozen_before_test': True, 'frozen_evaluation_code_unchanged': True,
              'selected_config': selection['selected_config'], 'retrieval_queries_rerun': False,
              'embedding_ledger_tokens_ingest_and_queries': total_tokens,
              'embedding_ledger_cost_usd_ingest_and_queries': round(total_cost, 10),
              'note': 'Saved trace/metric consistency only; no manual audit labels are inferred.'}
    (result / 'phase4_integrity.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
