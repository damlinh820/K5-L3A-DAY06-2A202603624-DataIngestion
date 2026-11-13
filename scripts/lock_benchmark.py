"""Freeze the user-approved benchmark and its corpus/protocol hashes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    approvals = json.loads((ROOT / 'data/approvals.json').read_text(encoding='utf-8'))
    if approvals['human_gate_2']['status'] != 'approved':
        raise SystemExit('Human Gate 2 is not approved')
    folder = ROOT / 'benchmark'
    if (folder / 'LOCK.json').exists():
        raise SystemExit('Benchmark already locked; do not rewrite it')
    questions = [json.loads(line) for line in (folder / 'questions.jsonl').read_text(encoding='utf-8').splitlines()]
    for q in questions:
        q['human_review'] = 'approved_via_gate_2'
    payload = ''.join(json.dumps(q, ensure_ascii=False) + '\n' for q in questions)
    (folder / 'questions.jsonl').write_text(payload, encoding='utf-8', newline='\n')
    protocol = json.loads((folder / 'protocol.json').read_text(encoding='utf-8'))
    protocol['status'] = 'locked_before_retrieval'
    (folder / 'protocol.json').write_text(json.dumps(protocol, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    review = (folder / 'REVIEW.md').read_text(encoding='utf-8')
    review = review.replace('> DRAFT: chưa có nhãn gold được học viên duyệt. Không chạy retrieval trước khi xác nhận Gate 2.',
                            '> GATE 2 ĐÃ ĐƯỢC XÁC NHẬN ngày 13/11/2026. Bộ câu hỏi được khóa trước retrieval; xem LOCK.json.')
    review = review.replace('**Học viên duyệt:** [ ]', '**Học viên duyệt:** [x] — xác nhận chung tại Gate 2')
    (folder / 'REVIEW.md').write_text(review, encoding='utf-8', newline='\n')
    lock = {'status': 'locked_before_retrieval', 'approved_on': '2026-11-13',
            'questions_sha256': sha(folder / 'questions.jsonl'),
            'protocol_sha256': sha(folder / 'protocol.json'),
            'pages_sha256': sha(ROOT / 'results/pages.jsonl'),
            'manifest_sha256': sha(ROOT / 'data/manifest.json'),
            'dev_ids': [q['id'] for q in questions if q['split'] == 'dev'],
            'test_ids': [q['id'] for q in questions if q['split'] == 'test'],
            'retrieval_run_before_lock': False}
    (folder / 'LOCK.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(lock))


if __name__ == '__main__':
    main()
