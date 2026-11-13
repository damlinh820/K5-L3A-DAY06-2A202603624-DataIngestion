"""Validate audit labels and summarize their disclosed human/AI origin."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'


def read_csv(name):
    with (RESULTS / name).open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    groups = {'coherence': read_csv('audit_coherence.csv'), 'metadata': read_csv('audit_metadata.csv'),
              'grounding': read_csv('audit_grounding.csv')}
    method_path = RESULTS / 'audit_method.json'
    method = json.loads(method_path.read_text(encoding='utf-8')) if method_path.exists() else {}
    origin = method.get('review_method', 'unspecified')
    expected = {'coherence': 30, 'metadata': 45, 'grounding': 15}
    pending, errors = [], []
    for kind, rows in groups.items():
        if len(rows) != expected[kind]:
            errors.append(f'{kind}: expected {expected[kind]} rows, found {len(rows)}')
        keys = []
        for row in rows:
            key = (row['config'], row.get('position_id', row.get('question_id')), row.get('rank', ''))
            keys.append(key)
            if origin == 'ai_assisted' and (row.get('label_origin') != origin or row.get('human_verified') != 'false'):
                errors.append(f'{kind}: inconsistent AI disclosure at {key}')
            if kind == 'metadata':
                if row['metadata_complete_correct_0_1'].strip() not in {'0', '1'}:
                    pending.append({'sheet': kind, 'key': key, 'field': 'metadata_complete_correct_0_1'})
                value = row['filter_compliant_0_1_or_NA'].strip()
                allowed = {'0', '1'} if json.loads(row['requested_filter']) else {'N/A'}
                if value not in allowed:
                    pending.append({'sheet': kind, 'key': key, 'field': 'filter_compliant_0_1_or_NA'})
                if row['metadata_complete_correct_0_1'].strip() == '0' and not row['reason'].strip():
                    pending.append({'sheet': kind, 'key': key, 'field': 'reason for metadata error'})
            else:
                if row['score_0_1_2'].strip() not in {'0', '1', '2'}:
                    pending.append({'sheet': kind, 'key': key, 'field': 'score_0_1_2'})
                if not row['reason'].strip():
                    pending.append({'sheet': kind, 'key': key, 'field': 'reason'})
        if len(keys) != len(set(keys)):
            errors.append(f'{kind}: duplicated row keys')
    for kind, rows in groups.items():
        per_config = Counter(row['config'] for row in rows)
        needed = {'coherence': 10, 'metadata': 15, 'grounding': 5}[kind]
        if dict(per_config) != {'A': needed, 'B': needed, 'C': needed}:
            errors.append(f'{kind}: invalid rows per config: {dict(per_config)}')
    status = {'status': 'complete' if not pending and not errors else 'pending_or_invalid',
              'rows': {key: len(value) for key, value in groups.items()}, 'errors': errors,
              'pending_fields': len(pending), 'pending': pending,
              'review_method': origin, 'human_verified': method.get('human_verified', False),
              'note': 'Summarizes recorded labels with disclosed origin; AI labels are not independent human judgments.'}
    (RESULTS / 'audit_status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in status.items() if key != 'pending'}))
    if pending or errors:
        if not args.check_only:
            raise SystemExit('Complete the audit labels and their provenance before requesting a summary.')
        return
    if args.check_only:
        return
    summary = {}
    for config in ['A', 'B', 'C']:
        coherence = [int(r['score_0_1_2']) for r in groups['coherence'] if r['config'] == config]
        grounding = [int(r['score_0_1_2']) for r in groups['grounding'] if r['config'] == config]
        meta = [r for r in groups['metadata'] if r['config'] == config]
        filtered_questions = {}
        for row in meta:
            if json.loads(row['requested_filter']):
                filtered_questions.setdefault(row['question_id'], []).append(int(row['filter_compliant_0_1_or_NA']))
        summary[config] = {'coherence': {'n': len(coherence), 'mean_out_of_2': sum(coherence) / len(coherence)},
            'metadata': {'correct_complete_count': sum(int(r['metadata_complete_correct_0_1']) for r in meta), 'total': len(meta)},
            'filter': {'query_count': len(filtered_questions),
                       'all_top3_compliant_queries': sum(len(v) == 3 and all(v) for v in filtered_questions.values())},
            'grounding': {'n': len(grounding), 'counts_0_1_2': {i: grounding.count(i) for i in range(3)},
                          'mean_out_of_2': sum(grounding) / len(grounding)}}
    summary['_method'] = {'review_method': origin, 'reviewer': method.get('reviewer', 'unspecified'),
                          'human_verified': method.get('human_verified', False),
                          'independent_human_labels': method.get('independent_human_labels', False),
                          'details': 'results/audit_method.json'}
    (RESULTS / 'audit_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # An accessible view of the actual labels; never regenerate or infer scores here.
    review = ['# Kết quả audit do AI hỗ trợ', '',
              'Người chấm: Codex theo yêu cầu “vậy bạn chấm giúp mình”. Chưa có xác minh của học viên; đây không phải nhãn thủ công độc lập. Phương pháp và hạn chế: [audit_method.json](audit_method.json).', '',
              '| Cấu hình | Coherence /2 (10 mẫu) | Metadata đúng-đủ | Filter: câu có đủ 3 hit đúng phạm vi | Grounding /2 (5 câu) | Grounding 0 / 1 / 2 |',
              '|---|---:|---:|---:|---:|---|']
    for config in ['A', 'B', 'C']:
        s = summary[config]
        counts = s['grounding']['counts_0_1_2']
        review.append(f"| {config} | {s['coherence']['mean_out_of_2']:.2f} | {s['metadata']['correct_complete_count']}/{s['metadata']['total']} | {s['filter']['all_top3_compliant_queries']}/{s['filter']['query_count']} | {s['grounding']['mean_out_of_2']:.2f} | {counts[0]} / {counts[1]} / {counts[2]} |")
    review += ['', 'Metadata đúng nguồn khác với bằng chứng đủ để trả lời. Q19 có yêu cầu phần 3: A/B trả cả ba hit ở phần 2; C chỉ có hit thứ ba đúng phạm vi. B+filter là thí nghiệm riêng, không thay điểm của A/B/C chính.', '',
               'Các nhãn được xem sau khi đã có điểm retrieval, cùng assistant viết pipeline và chấm nên có nguy cơ thiên lệch. Không thay đổi lựa chọn C đã khóa trước test.', '', '## Coherence — 30 mẫu', '']
    for row in groups['coherence']:
        review += [f"- **{row['config']} / {row['position_id']} / Điều {row['article']} — {row['score_0_1_2']}/2:** {row['reason']}"]
    review += ['', '## Grounding — 15 đánh giá', '']
    for row in groups['grounding']:
        review += [f"### {row['config']} / {row['question_id']} — {row['score_0_1_2']}/2", '', row['question'], '', row['reason'], '']
    review += ['## Metadata — 45 bản ghi', '',
               'Đã trích xuất lại text layer ở 22 trang PDF liên quan (kể cả trang gold test), kiểm tra hash PDF và offset nguồn. Đây là kiểm tra text/provenance, không phải kiểm tra bố cục bằng mắt hoặc xác minh pháp luật hiện hành. Xem [ai_audit_source_checks.json](ai_audit_source_checks.json).', '']
    for row in groups['metadata']:
        review.append(f"- **{row['config']} / {row['question_id']} / rank {row['rank']}:** metadata {row['metadata_complete_correct_0_1']}; filter {row['filter_compliant_0_1_or_NA']}. {row['reason']}")
    (RESULTS / 'AUDIT_REVIEW.md').write_text('\n'.join(review) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
