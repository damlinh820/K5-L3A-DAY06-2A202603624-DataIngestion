"""Prepare unlabelled source-audit sheets and actual failure/filter summaries."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'


def traces(name):
    return [json.loads(line) for line in (RESULTS / f'trace_{name}.jsonl').read_text(encoding='utf-8').splitlines()]


def write_csv_if_missing(path, rows):
    if path.exists():
        return
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    test_run = json.loads((RESULTS / 'test_run.json').read_text(encoding='utf-8'))
    if test_run['status'] != 'complete':
        raise SystemExit('Finish the locked test evaluation before preparing these sheets')
    metadata_rows, grounding_rows = [], []
    failures = ['# Trường hợp thiếu evidence theo kiểm tra tự động', '',
                'Các mục dưới đây lấy từ trace thật. Không phải nhãn coherence/grounding của người chấm. Không dùng kết quả test để chỉnh cấu hình.', '']
    for config in ['A', 'B', 'C']:
        for trace in traces(config):
            if not trace['evidence_hit_at_3']:
                failures.extend([f"## {config} / {trace['split']} / {trace['id']}", '', trace['question'], '',
                                 'Nguồn gold: ' + ', '.join(f"{g['source_id']}.pdf:{g['page']}" for g in trace['gold_evidence']), '',
                                 f"Evidence bị chia qua top-3 (chỉ số bổ sung): {trace['evidence_split_across_top3']}", ''])
                for hit in trace['hits']:
                    failures.extend([f"- Rank {hit['rank']}: `{hit['chunk_id']}`, Điều {hit['article']}, Khoản {hit['clause']}; `{hit['document_id']}.pdf:{hit['page']}–{hit['page_end']}`.",
                                     '  Trích đầu chunk: ' + hit['text'][:350].replace('\n', ' ')])
                failures.append('')
            if trace['split'] != 'test':
                continue
            top3 = trace['hits'][:3]
            for rank in range(1, 4):
                hit = top3[rank - 1] if rank <= len(top3) else None
                metadata_rows.append({'config': config, 'question_id': trace['id'], 'question': trace['question'],
                    'rank': rank, 'chunk_id': hit['chunk_id'] if hit else '',
                    'document_id': hit['document_id'] if hit else '', 'source_url': hit['source'] if hit else '',
                    'page': hit['page'] if hit else '', 'page_end': hit['page_end'] if hit else '',
                    'metadata_json': json.dumps(hit['metadata'], ensure_ascii=False) if hit else '{}',
                    'provenance_json': json.dumps(hit['provenance'] + hit.get('context_provenance', []), ensure_ascii=False) if hit else '[]',
                    'text': hit['text'] if hit else '',
                    'requested_filter': json.dumps(trace['requested_filter'], ensure_ascii=False),
                    'applied_filter': json.dumps(trace['applied_filter'], ensure_ascii=False),
                    'metadata_complete_correct_0_1': '', 'filter_compliant_0_1_or_NA': '', 'reason': ''})
            grounding_rows.append({'config': config, 'question_id': trace['id'], 'question': trace['question'],
                'expected_answer': trace['expected_answer'], 'gold_evidence_json': json.dumps(trace['gold_evidence'], ensure_ascii=False),
                'top3_chunk_ids': json.dumps([h['chunk_id'] for h in top3]),
                'top3_json': json.dumps([{k: h[k] for k in ['rank', 'text', 'source', 'page', 'page_end', 'provenance', 'context_provenance']}
                                        for h in top3], ensure_ascii=False),
                'score_0_1_2': '', 'reason': ''})
    write_csv_if_missing(RESULTS / 'audit_metadata.csv', metadata_rows)
    write_csv_if_missing(RESULTS / 'audit_grounding.csv', grounding_rows)
    (RESULTS / 'failure_cases.md').write_text('\n'.join(failures) + '\n', encoding='utf-8')

    baseline, filtered = {t['id']: t for t in traces('B_filter_baseline')}, {t['id']: t for t in traces('B_filter')}
    pairs = []
    for query_id, old in baseline.items():
        new = filtered[query_id]
        pairs.append({'id': query_id, 'split': old['split'], 'filter': old['requested_filter'],
                      'baseline_hit_at_1': old['hit_at_1'], 'filtered_hit_at_1': new['hit_at_1'],
                      'baseline_hit_at_3': old['evidence_hit_at_3'], 'filtered_hit_at_3': new['evidence_hit_at_3'],
                      'baseline_scope_compliant': old['requested_scope_satisfied_by_all_top3'],
                      'filtered_scope_compliant': new['requested_scope_satisfied_by_all_top3']})
    (RESULTS / 'filter_comparison.json').write_text(json.dumps({'pairs': pairs,
        'note': 'Same B index/model/query vectors; only explicit user-provided part filter changes. Scope compliance is a metadata-value check, not a manual source audit.'},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {'status': 'retrieval_complete_manual_audit_pending', 'selected_config': test_run['selected_config_frozen_before_test'],
               'metadata_rows': len(metadata_rows), 'grounding_rows': len(grounding_rows),
               'coherence_rows': 30, 'human_labels_generated_by_agent': False,
               'dev_selection': 'results/dev_selection.json', 'test_run': 'results/test_run.json'}
    method_path = RESULTS / 'audit_method.json'
    if method_path.exists():
        method = json.loads(method_path.read_text(encoding='utf-8'))
        summary.update({'status': 'retrieval_complete_audit_recorded',
                        'audit_review_method': method['review_method'],
                        'human_verified': method['human_verified'],
                        'audit_method': 'results/audit_method.json'})
    (RESULTS / 'phase4_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
