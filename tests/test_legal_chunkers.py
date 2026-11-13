import unittest
import hashlib
import json

from src.chunkers import clause_boundaries, fixed, heading, hybrid, units
from src.extract import ROOT, load_corpus, matches_snapshot
from src.normalize import normalize


class LegalChunkersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text, cls.spans = load_corpus()
        cls.a = fixed(cls.text, cls.spans)
        cls.b = heading(cls.text, cls.spans)
        cls.c = hybrid(cls.text, cls.spans)

    def test_fixed_covers_entire_text_with_no_unicode_corruption(self):
        self.assertEqual(self.a[0]['body_start'], 0)
        self.assertEqual(self.a[-1]['body_end'], len(self.text))
        for i, c in enumerate(self.a):
            self.assertEqual(c['text'], self.text[c['body_start']:c['body_end']])
            self.assertNotIn('\ufffd', c['text'])
            self.assertLessEqual(c['token_end'] - c['token_start'], 512)
            if i:
                self.assertLessEqual(c['body_start'], self.a[i - 1]['body_end'])
                self.assertGreater(c['body_end'], self.a[i - 1]['body_end'])
        self.assertEqual([c['chunk_id'] for c in self.a], [c['chunk_id'] for c in fixed(self.text, self.spans)])

    def test_every_original_article_once_and_context_preserved(self):
        ids = [int(c['article']) for c in self.b if c['article'] is not None]
        self.assertEqual(ids, list(range(1, 261)))
        self.assertTrue(any(c['article'] is None for c in self.b))
        self.assertEqual(''.join(c['text'] for c in self.b), self.text)

    def test_hybrid_keeps_all_article_body_and_heading_context(self):
        for u in units(self.text, self.spans):
            chunks = [c for c in self.c if c['body_start'] >= u['start'] and c['body_end'] <= u['end']]
            if len(chunks) == 1 and not chunks[0]['prefix']:
                self.assertEqual(chunks[0]['text'], u['text'])
            else:
                original_heading = u['text'].partition('\n')[0] + '\n'
                self.assertTrue(all(c['prefix'] == original_heading for c in chunks))
                recovered = original_heading + ''.join(self.text[c['body_start']:c['body_end']] for c in chunks)
                self.assertEqual(recovered, u['text'])
        self.assertEqual({c['article'] for c in self.b}, {c['article'] for c in self.c})

    def test_source_spans_cover_body_without_gaps(self):
        for c in self.a + self.b + self.c:
            p = c['provenance']
            self.assertEqual(p[0]['start'], c['body_start'])
            self.assertEqual(p[-1]['end'], c['body_end'])
            for left, right in zip(p, p[1:]):
                self.assertEqual(left['end'], right['start'])

    def test_nested_quoted_clauses_are_not_original_clauses(self):
        text = '1. Sửa như sau:\n“Điều 9. Nội dung\n1. Trích dẫn\n2. Trích dẫn tiếp.”\n2. Khoản gốc tiếp theo\n'
        self.assertEqual([number for _, number in clause_boundaries(text)], ['1', '2'])

    def test_reflow_keeps_markers_and_joins_wrapped_sentences(self):
        raw = 'CÔNG BÁO/Số 1\nĐiều 1. Tên điều\n1. Một câu\nbị xuống dòng.\na) Một điểm\ncũng xuống dòng.\n2. Khoản khác\n'
        self.assertEqual(normalize(raw), 'Điều 1. Tên điều\n1. Một câu bị xuống dòng.\na) Một điểm cũng xuống dòng.\n2. Khoản khác')

    def test_git_line_endings_do_not_unlock_content_changes(self):
        original = b'line one\r\nline two\r\n'
        digest = hashlib.sha256(original).hexdigest()
        self.assertTrue(matches_snapshot(original.replace(b'\r\n', b'\n'), digest))
        self.assertFalse(matches_snapshot(b'line one\nchanged content\n', digest))

    def test_reflow_preserves_every_locked_gold_quote_on_its_source_page(self):
        by_page = {(s['document_id'], s['page']): self.text[s['start']:s['end']] for s in self.spans}
        fold = lambda value: ' '.join(value.split())
        for line in (ROOT / 'benchmark/questions.jsonl').read_text(encoding='utf-8').splitlines():
            question = json.loads(line)
            for gold in question['gold_evidence']:
                self.assertIn(fold(gold['evidence_quote']), fold(by_page[(gold['source_id'], gold['page'])]))


if __name__ == '__main__':
    unittest.main()
