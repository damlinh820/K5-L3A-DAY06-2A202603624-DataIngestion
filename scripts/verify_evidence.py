"""Validate benchmark provenance and exact evidence; semantic gold remains human-reviewed."""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text)).strip()


def main():
    target = ROOT / 'benchmark/questions.jsonl'
    data = target.read_bytes()
    questions = [json.loads(line) for line in data.decode('utf-8').splitlines() if line.strip()]
    pages = [json.loads(line) for line in (ROOT / 'results/pages.jsonl').read_text(encoding='utf-8').splitlines()]
    lookup = {(p['source_id'], p['page']): p for p in pages}
    errors, checks = [], []
    ids = [q['id'] for q in questions]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate question IDs')
    splits = Counter(q['split'] for q in questions)
    if len(questions) < 20 or splits['dev'] < 15 or splits['test'] < 5:
        errors.append('Need >=20 questions, >=15 dev, >=5 test')
    filtered = [q for q in questions if q['filter']]
    if len(filtered) < 3 or not any(q['split'] == 'test' for q in filtered):
        errors.append('Need >=3 explicit filter queries including >=1 test')
    for q in questions:
        golds = q['gold_evidence']
        assert golds, f"{q['id']} has no gold"
        primary_found = False
        for gold in golds:
            p = lookup.get((gold['source_id'], gold['page']))
            quote = norm(gold['evidence_quote'])
            ok = bool(p and quote and quote in norm(p['text']))
            checks.append({'id': q['id'], 'source_id': gold['source_id'], 'page': gold['page'], 'quote_found': ok})
            if not ok:
                errors.append(f"{q['id']}: missing evidence at {gold['source_id']}:{gold['page']}")
            primary_found |= (gold['source_id'], gold['page']) == (q['gold_source_id'], q['gold_page'])
        if not primary_found:
            errors.append(f"{q['id']}: primary evidence not listed among accepted golds")
        if q['filter']:
            if set(q['filter']) != {'part'}:
                errors.append(f"{q['id']}: unexpected draft filter key")
            part = q['filter'].get('part')
            if f'phần {part}' not in q['question'].lower():
                errors.append(f"{q['id']}: filter not explicitly provided in question")
            if not any(lookup[(g['source_id'], g['page'])]['part'] == part for g in golds):
                errors.append(f"{q['id']}: filter excludes every documented gold")
    report = {'status': 'passed' if not errors else 'failed', 'questions': len(questions),
              'splits': dict(splits), 'filter_questions': len(filtered),
              'test_filter_questions': sum(q['split'] == 'test' for q in filtered),
              'benchmark_sha256': hashlib.sha256(data).hexdigest(),
              'errors': errors, 'checks': checks,
              'limitation': 'Exact evidence/provenance validation only. Expected-answer adequacy and legal conditions require student review at Gate 2.'}
    (ROOT / 'results/evidence_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
