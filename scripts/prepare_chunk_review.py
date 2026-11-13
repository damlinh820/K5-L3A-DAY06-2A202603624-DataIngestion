"""Create Gate 3 examples and preselect coherence positions before retrieval."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.chunkers import units
from src.extract import load_corpus, provenance


def main():
    approvals = json.loads((ROOT / 'data/approvals.json').read_text(encoding='utf-8'))
    if approvals['human_gate_3']['status'] == 'approved':
        raise SystemExit('Gate 3 already approved; preserve the reviewed examples and existing audit positions.')
    text, spans = load_corpus()
    articles = {u['article']: u for u in units(text, spans) if u['article']}
    chunks = {config: [json.loads(line) for line in (ROOT / f'results/chunks_{config}.jsonl').read_text(encoding='utf-8').splitlines()]
              for config in ['A', 'B', 'C']}

    def anchor(article):
        u = articles[str(article)]
        heading_end = u['start'] + len(u['text'].partition('\n')[0]) + 1
        return min(heading_end + 80, u['end'] - 1)

    def covering(config, offset):
        found = [c for c in chunks[config] if c['body_start'] <= offset < c['body_end']]
        if not found:
            raise ValueError('No chunk covers the fixed source position')
        return max(found, key=lambda c: (c['body_start'], c['chunk_id']))

    positions, rows = [], []
    for i, article in enumerate([1, 30, 59, 88, 117, 146, 175, 204, 233, 260], 1):
        offset = anchor(article)
        source = provenance(spans, offset, offset + 1)[0]
        position = {'position_id': f'position_{i:02d}', 'article': article,
                    'corpus_character_offset': offset, 'source_id': source['document_id'], 'page': source['page']}
        positions.append(position)
        for config in ['A', 'B', 'C']:
            c = covering(config, offset)
            rows.append({**position, 'config': config, 'chunk_id': c['chunk_id'], 'text': c['text'],
                         'score_0_1_2': '', 'reason': ''})
    path = ROOT / 'results/audit_positions.json'
    if path.exists() and json.loads(path.read_text(encoding='utf-8')) != positions:
        raise RuntimeError('Previously chosen audit positions changed')
    path.write_text(json.dumps(positions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    audit = ROOT / 'results/audit_coherence.csv'
    if not audit.exists():
        with audit.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    review = ['# Gate 3 — chunk mẫu cần học viên duyệt', '',
              'Đây là mẫu chunk trước retrieval. Chưa có điểm Hit@1/Hit@3 hoặc nhãn audit.', '',
              'A: cửa sổ 512 token/overlap 64; biên token được điều chỉnh nhẹ để không cắt ký tự UTF-8.',
              'B: mỗi Điều nguyên vẹn, giữ cả phần mở đầu/Chương/Mục thành đơn vị riêng.',
              'C: Điều dài hơn 512 token được tách Khoản và lặp lại tiêu đề Điều. Khoản dài vẫn được giữ trọn nên chunk C có thể vượt 512 token; không bị cắt cụt.', '',
              'Cần xem: có giữ đúng Điều/Khoản không; nội dung có bị mất hay lẫn Chương khác không; source/page và phần nối qua trang có truy vết đúng không.', '',
              'Các đoạn mẫu dưới đây được chọn theo Điều 3, 91, 172 để phủ ba phần PDF, không dựa trên điểm retrieval. Mười vị trí coherence được định trước trong audit_positions.json; bảng audit_coherence.csv có 30 dòng nhãn trống để chấm sau.', '']

    def append_chunk(title, c):
        refs = sorted({(p['document_id'], p['page']) for p in c['provenance'] + c['context_provenance']})
        review.extend([f'## {title}', '',
                       f"Chunk `{c['chunk_id']}`; {c['n_tokens']} token; Điều `{c['article']}`; Khoản `{c['clause']}`; Chương `{c['chapter']}`.", '',
                       'Nguồn/trang: ' + ', '.join(f'`{s}.pdf:{p}`' for s, p in refs), '',
                       '```text', c['text'].rstrip(), '```', '', 'Học viên duyệt: [ ]', ''])

    for article in [3, 91, 172]:
        for config in ['A', 'B', 'C']:
            append_chunk(f'Điều {article} — cấu hình {config}', covering(config, anchor(article)))
    append_chunk('Bổ sung: Khoản dài nhất của C (kiểm tra giữ nguyên đơn vị)', max(chunks['C'], key=lambda c: c['n_tokens']))
    (ROOT / 'results/CHUNK_REVIEW.md').write_text('\n'.join(review) + '\n', encoding='utf-8')
    print('Prepared 10 chunk examples and 30 blank coherence rows; Gate 3 remains pending.')


if __name__ == '__main__':
    main()
