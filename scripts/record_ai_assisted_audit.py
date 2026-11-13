"""Record disclosed assistant judgments, supported by a fresh local PDF/source check.

The score/reason tables below were authored after reading the selected chunk texts
and question/top-3 records. They are not human labels or an automatic Hit@3 mapping.
Run once; never overwrite an existing assessment.
"""
import csv
import hashlib
import json
import re
import sys
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extract import load_corpus
from src.normalize import normalize
from scripts.prepare_legal_corpus import normalize as page_normalize

RESULTS = ROOT / 'results'

# Same rubric for every configuration: 1 when the chunk has intelligible complete
# content but also severed clauses, 2 when its legal unit is intact. Cross-references
# alone do not make an otherwise intact legal unit incoherent.
COHERENCE_A = [
    'Giữ trọn Điều 1–2 nhưng kết thúc giữa từ ở khoản 1 Điều 3 ("Bản đồ đ"); chunk chỉ mạch lạc một phần.',
    'Có đủ tiêu đề và khoản 1 Điều 30; đầu còn đuôi Điều trước, cuối cắt khoản 2 tại "khấu trừ vào tiền".',
    'Điều 59 khoản 1–5 đọc được; đầu là đuôi Điều 58, khoản 6 bị cắt ở "hằng", thiếu phần thời hạn công bố.',
    'Giữ khoản 1 Điều 88 nhưng lẫn đuôi Điều trước; điểm a khoản 2 bị cắt giữa tên cơ quan, thiếu điều kiện hoàn chỉnh.',
    'Nội dung Điều 117 còn hiểu được nhưng mất đầu tiêu đề; sang Điều 118 và cắt giữa cụm "đất cơ s".',
    'Tiêu đề và khoản 1 Điều 146 đầy đủ; đầu còn đuôi Điều trước, khoản 2 bị cắt giữa từ "hoặ", thiếu phạm vi cấm cấp giấy.',
    'Điều 175 khoản 1 có đủ sáu điều kiện; đầu lẫn Điều 174 và khoản 2 bị cắt ở "quy định t", mất dẫn chiếu thời hạn.',
    'Điều 204 khoản 1–2 có ý hoàn chỉnh; đầu là đuôi Điều trước, cuối chỉ còn "3. Người", thiếu chủ thể và nội dung khoản 3.',
    'Có tiêu đề và phần dẫn khoản 1 Điều 233; đầu là đuôi Điều 232, điểm a bị cắt ở "sử d", danh mục thông tin chưa đủ.',
    'Có tiêu đề Điều 260 nhưng khoản 1 bị cắt tại "quyền và nghĩa vụ qu", mất dẫn chiếu cho hộ gia đình/cá nhân; đầu còn Điều 259.',
]

COHERENCE_B = [
    'Trọn Điều 1: có tiêu đề và câu xác định phạm vi điều chỉnh, không đứt ý.',
    'Trọn Điều 30 với ba khoản lựa chọn hình thức trả tiền thuê đất; các chủ thể, điều kiện và hệ quả được giữ nguyên.',
    'Trọn Điều 59, đủ chín khoản trách nhiệm, thời hạn công bố/báo cáo và kinh phí; không cắt giữa câu.',
    'Trọn Điều 88, đủ nguyên tắc, điều kiện, thẩm quyền, trình tự cưỡng chế và trách nhiệm; các điểm liên kết đúng khoản.',
    'Trọn Điều 117, giữ quy tắc và ngoại lệ chuyển nhượng dự án; tiêu đề dính thân câu do reflow nhưng vẫn rõ nghĩa.',
    'Trọn Điều 146 với ba khoản điều kiện cấp giấy/tách thửa; giữ các dẫn chiếu Điều 220, không cắt giữa câu.',
    'Trọn Điều 175, đủ sáu điều kiện và khoản giới hạn thời hạn có dẫn chiếu; cần đọc Điều 172 nếu muốn biết con số cụ thể.',
    'Trọn Điều 204 với sáu khoản về khu công nghệ cao, thời hạn và quyền/nghĩa vụ; không đứt danh mục.',
    'Trọn Điều 233, đủ danh mục thông tin, trách nhiệm cập nhật và công khai; không cắt giữa ý.',
    'Giữ đủ 16 khoản chuyển tiếp Điều 260; dài và có lời thông qua/chữ ký cuối văn bản nhưng các trường hợp pháp lý không bị cắt.',
]

COHERENCE_C = [
    COHERENCE_B[0],
    'Có tiêu đề Điều 30 và trọn khoản 1: đủ chủ thể, điều kiện chuyển hình thức thuê, thời điểm xác định giá và phần thời gian còn lại.',
    'Có tiêu đề Điều 59 và trọn khoản 1 xác định trách nhiệm tổ chức/phê duyệt của UBND các cấp; tự hiểu được đơn vị trách nhiệm này.',
    'Có tiêu đề Điều 88 và trọn khoản 1, gồm đủ điểm a–b về nguyên tắc và giờ bắt đầu cưỡng chế; không cắt danh mục.',
    COHERENCE_B[4],
    'Có tiêu đề Điều 146 và trọn khoản 1, giữ điều kiện thời điểm hình thành, diện tích và điều kiện được cấp giấy.',
    COHERENCE_B[6],
    'Có tiêu đề Điều 204 và trọn khoản 1, giữ định nghĩa, yêu cầu quy hoạch và công trình phục vụ người lao động.',
    'Có tiêu đề Điều 233 và trọn khoản 1 với đủ điểm a–đ; chỉ là đơn vị danh mục thông tin, không phải toàn bộ trách nhiệm của Điều.',
    'Có tiêu đề Điều 260 và trọn khoản 1; giữ mốc 01/7/2004, ít nhất 05 năm còn lại và dẫn chiếu quyền/nghĩa vụ riêng cho từng chủ thể.',
]

GROUNDING = {
    ('A', 'q16'): (2, 'Rank 1 có tiêu đề Điều 171 và khoản 1 "Đất ở", đủ xác định ổn định lâu dài; nguồn phần 3 trang 1.'),
    ('B', 'q16'): (2, 'Rank 1 giữ trọn Điều 171, khoản 1 nêu Đất ở dưới tiêu đề Đất sử dụng ổn định lâu dài; phần 3 trang 1.'),
    ('C', 'q16'): (2, 'Rank 3 có Điều 171 khoản 1, đủ kết luận đất ở sử dụng ổn định lâu dài, phần 3 trang 1; hai rank đầu không trả lời câu hỏi.'),
    ('A', 'q17'): (2, 'Rank 3 chứa trọn điểm a khoản 1 Điều 172: đúng cá nhân trực tiếp sản xuất, loại đất và hạn mức, 50 năm và tiếp tục không làm thủ tục gia hạn; phần 3 trang 2.'),
    ('B', 'q17'): (1, 'Rank 3 Điều 174 nói tiếp tục sử dụng không làm thủ tục gia hạn nhưng cho trường hợp NHẬN CHUYỂN QUYỀN, khác giao/công nhận đang hỏi; chỉ dẫn Điều 172, không có 50 năm. Không đủ để trả lời trọn câu.'),
    ('C', 'q17'): (0, 'Cả ba hit là Điều 176 về HẠN MỨC diện tích, không có bằng chứng về thời hạn 50 năm hoặc miễn thủ tục gia hạn của Điều 172.'),
    ('A', 'q18'): (1, 'Rank 1 chỉ giữ đuôi điểm b "ụng, đất rừng phòng hộ ... ổn định lâu dài", mất điều kiện chuyển TỪ đất trồng cây hằng năm SANG rừng đặc dụng; hai hit còn lại nói hạn mức. Có mảnh kết luận nhưng thiếu tiền đề.'),
    ('B', 'q18'): (2, 'Rank 1 Điều 173 khoản 1 điểm b giữ đủ loại đất trước/sau chuyển mục đích và kết luận ổn định lâu dài; phần 3 trang 3.'),
    ('C', 'q18'): (2, 'Rank 1 giữ tiêu đề Điều 173 và toàn khoản 1, điểm b đủ tiền đề chuyển đất trồng cây hằng năm sang rừng đặc dụng và kết luận ổn định lâu dài; phần 3 trang 3.'),
    ('A', 'q19'): (0, 'Cả ba hit ở phần 2, sai phạm vi phần 3; nói cấp giấy nhiều xã, thu hồi/cấp đổi giấy và giấy tờ lịch sử, không có điều kiện tại Điều 220 khoản 1 điểm a.'),
    ('B', 'q19'): (1, 'Rank 1 Điều 146 khoản 3 có cùng bốn loại giấy và dẫn Điều 220, nhưng ở phần 2, cho trường hợp cấp lại sau tách/hợp; thiếu chính điều kiện Điều 220 trong phần 3 được yêu cầu. Không đủ grounding theo phạm vi câu hỏi.'),
    ('C', 'q19'): (2, 'Rank 3 đúng Điều 220 khoản 1 điểm a ở phần 3 trang 34, giữ đủ bốn loại giấy chứng nhận. Hai hit đầu sai phạm vi được ghi lỗi filter riêng; không xóa bằng chứng hợp lệ ở rank 3.'),
    ('A', 'q20'): (2, 'Rank 2 giữ trọn điểm c khoản 2 Điều 235: không quá 30 ngày kể từ ngày nhận đơn yêu cầu hòa giải, phần 3 trang 46; rank 1 bị cắt chưa đủ nhưng top-3 đủ.'),
    ('B', 'q20'): (2, 'Rank 1 có trọn Điều 235; điểm c khoản 2 nêu đủ 30 ngày và mốc nhận đơn, phần 3 trang 46. Không nhầm 30 ngày trưng dụng ở rank 2.'),
    ('C', 'q20'): (2, 'Rank 3 giữ Điều 235 khoản 2 điểm c, đủ thời hạn và mốc tính tại phần 3 trang 46; phân biệt với 30 ngày thực hiện quyết định tranh chấp ở rank 1 và 30 ngày làm việc đăng ký sau hòa giải ở rank 2.'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    names = ['audit_coherence.csv', 'audit_metadata.csv', 'audit_grounding.csv']
    tables = {}
    for name in names:
        with (RESULTS / name).open(encoding='utf-8-sig', newline='') as stream:
            tables[name] = list(csv.DictReader(stream))
        if any(r.get('score_0_1_2', '').strip() or r.get('metadata_complete_correct_0_1', '').strip()
               for r in tables[name]):
            raise SystemExit(f'Existing labels in {name}; refusing to overwrite an assessment.')

    corpus, spans = load_corpus()
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    documents = {d['document_id']: d for d in manifest['documents']}
    pages = {(p['source_id'], p['page']): p for p in map(json.loads, (RESULTS / 'pages.jsonl').read_text(encoding='utf-8').splitlines())}
    chunks = {config: {c['chunk_id']: c for c in map(json.loads, (RESULTS / f'chunks_{config}.jsonl').read_text(encoding='utf-8').splitlines())}
              for config in ['A', 'B', 'C']}
    metadata_rows = tables['audit_metadata.csv']
    required_pages = {(p['document_id'], p['page']) for r in metadata_rows for p in json.loads(r['provenance_json'])}
    for q in map(json.loads, (ROOT / 'benchmark/questions.jsonl').read_text(encoding='utf-8').splitlines()):
        if q['split'] == 'test':
            required_pages.update((g['source_id'], g['page']) for g in q['gold_evidence'])
    # Source/text comparisons, not a visual/page-layout or current-law review.
    with ExitStack() as stack:
        pdfs = {}
        for doc, info in documents.items():
            path = ROOT / info['local_path']
            assert sha(path) == info['sha256'], f'PDF hash changed: {doc}'
            pdfs[doc] = stack.enter_context(pdfplumber.open(path))
        for doc, page in sorted(required_pages):
            extracted = pdfs[doc].pages[page - 1].extract_text(layout=False) or ''
            assert page_normalize(extracted) == pages[(doc, page)]['text'], (doc, page)

    checks = []
    for r in metadata_rows:
        m = json.loads(r['metadata_json'])
        chunk = chunks[r['config']][r['chunk_id']]
        body = chunk['provenance']
        errors = []
        def check(condition, message):
            if not condition:
                errors.append(message)
        check(chunk['text'] == r['text'] == chunk['prefix'] + corpus[chunk['body_start']:chunk['body_end']], 'text/body mismatch')
        check(json.loads(r['provenance_json']) == body + chunk['context_provenance'], 'sheet provenance mismatch')
        check(json.loads(m['provenance_json']) == body and json.loads(m['context_provenance_json']) == chunk['context_provenance'], 'metadata provenance mismatch')
        for p in body + chunk['context_provenance']:
            check(any(s['document_id'] == p['document_id'] and s['page'] == p['page'] and
                      s['start'] <= p['start'] < p['end'] <= s['end'] for s in spans), 'invalid source/page interval')
            check(p['part'] == documents[p['document_id']]['part'] and p['source'] == documents[p['document_id']]['source_path_or_url'], 'incorrect source/part')
        check(m['document_id'] == r['document_id'] == body[0]['document_id'], 'incorrect document_id')
        check(m['source'] == r['source_url'] == body[0]['source'], 'incorrect source URL')
        check(int(r['page']) == m['page'] == body[0]['page'] and int(r['page_end']) == m['page_end'] == body[-1]['page'], 'incorrect body page range')
        check(m['part'] == body[0]['part'], 'incorrect filterable part')
        # Read source headings independently of the chunk parser.
        if m.get('article'):
            location = chunk['context_provenance'][0]['start'] if chunk['prefix'] else chunk['body_start']
            header = re.match(r'Điều\s+(\d+[a-z]?)\.', corpus[location:])
            check(header is not None and header[1] == m['article'], 'incorrect article')
            chapters = list(re.finditer(r'^Chương\s+([IVXLCDM]+)\b', corpus[:location], re.M))
            chapter = chapters[-1] if chapters else None
            check(chapter is not None and chapter[1] == m.get('chapter'), 'incorrect chapter')
            sections = list(re.finditer(r'^Mục\s+(\d+)\b', corpus[chapter.start() if chapter else 0:location], re.M))
            check((sections[-1][1] if sections else None) == m.get('section'), 'incorrect section')
        if m.get('clause'):
            check(corpus[chunk['body_start']:].startswith(m['clause'] + '. '), 'incorrect clause')
        r['metadata_complete_correct_0_1'] = str(int(not errors))
        requested = json.loads(r['requested_filter'])
        scope_ok = all(p.get(k) == value for p in body + chunk['context_provenance'] for k, value in requested.items())
        r['filter_compliant_0_1_or_NA'] = str(int(scope_ok)) if requested else 'N/A'
        location_note = f"{r['document_id']}.pdf trang thân {r['page']}–{r['page_end']}"
        structure = f"; Điều {m['article']}" if m.get('article') else '; A không có nhãn Điều, không phải trường bắt buộc'
        if m.get('clause'):
            structure += f", khoản {m['clause']}; tiêu đề lặp có provenance riêng"
        scope_note = (f"; yêu cầu part={requested['part']}, toàn bộ nguồn chunk {'đúng' if scope_ok else 'sai'} phạm vi" if requested else '; không yêu cầu filter: N/A')
        r['reason'] = ('Đã đối chiếu text layer PDF và khoảng provenance; ' + location_note + structure + scope_note
                       if not errors else 'Lỗi: ' + '; '.join(errors))
        checks.append({'config': r['config'], 'question_id': r['question_id'], 'rank': int(r['rank']),
                       'errors': errors, 'source_page_intervals': json.loads(r['provenance_json']),
                       'requested_scope_satisfied': scope_ok if requested else None})

    for r in tables['audit_coherence.csv']:
        i = int(r['position_id'][-2:]) - 1
        r['score_0_1_2'] = '1' if r['config'] == 'A' else '2'
        r['reason'] = {'A': COHERENCE_A, 'B': COHERENCE_B, 'C': COHERENCE_C}[r['config']][i]
    for r in tables['audit_grounding.csv']:
        score, reason = GROUNDING[(r['config'], r['question_id'])]
        r['score_0_1_2'], r['reason'] = str(score), reason

    original_hashes = {name: sha(RESULTS / name) for name in names}
    backup = RESULTS / 'audit_before_ai'
    backup.mkdir(exist_ok=True)
    for name in names:
        target = backup / name
        if target.exists():
            raise SystemExit('Backup already exists; stop to preserve audit history.')
        target.write_bytes((RESULTS / name).read_bytes())
    for name, rows in tables.items():
        for row in rows:
            row.update({'label_origin': 'ai_assisted', 'reviewer': 'Codex', 'human_verified': 'false'})
        with (RESULTS / name).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    method = {'review_method': 'ai_assisted', 'reviewer': 'Codex conversational assistant',
              'model_version': 'Not exposed in this session; no guessed model identifier',
              'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
              'authorization': 'User message: vậy bạn chấm giúp mình',
              'supersedes_plan_gate_4_actor': True, 'human_verified': False,
              'independent_human_labels': False, 'blind_to_retrieval_scores': False,
              'rubric': 'GUIDE.md sections 4.2–4.4; 0/1/2 coherence and grounding, 0/1 metadata, query-level all-top3 filter',
              'procedure': ['Assistant read all 30 coherence chunks and 15 question/top-3 audit records, including shared chunks.',
                            'Fresh local text-layer extraction checked PDF source pages against the locked extraction; no visual or current-law review.',
                            'Metadata labels supported by source offsets, body/context page ranges and independently scanned legal headings.',
                            'Grounding considers premises, exceptions, question scope and all top-3; not inferred from Hit@3.',
                            'Partial grounding: relevant fragment/related rule without the requested premise or valid scope scores 1; unrelated results score 0.',
                            'No retrieval rerun, no changes to gold, benchmark, chunk snapshot, model or selected configuration.'],
              'limitations': ['Same assistant implemented the pipeline and reviewed it; labels are not independent and were not blinded.',
                              'No student verification of these labels is claimed; human checking remains advisable under GUIDE.',
                              'Only the prescribed 30/45/15 audit rows; no claim about all 253 pages or current legal validity.'],
              'extra_embedding_or_generation_api_calls': 0,
              'original_sheet_sha256': original_hashes,
              'labelled_sheet_sha256': {name: sha(RESULTS / name) for name in names},
              'rubric_sha256': sha(ROOT / 'GUIDE.md')}
    (RESULTS / 'audit_method.json').write_text(json.dumps(method, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (RESULTS / 'ai_audit_source_checks.json').write_text(json.dumps({'pdf_pages_reextracted': len(required_pages),
        'pdf_source_hashes_match_manifest': True, 'metadata_records': len(checks),
        'records_with_errors': sum(bool(r['errors']) for r in checks), 'checks': checks}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'label_origin': 'ai_assisted', 'human_verified': False, 'rows': {k: len(v) for k, v in tables.items()},
                      'pdf_pages_reextracted': len(required_pages), 'metadata_records_with_errors': sum(bool(r['errors']) for r in checks)}))


if __name__ == '__main__':
    main()
