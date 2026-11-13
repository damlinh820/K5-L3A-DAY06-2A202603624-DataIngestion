"""Tiny text-only fixtures check metric logic; no mock embeddings or API calls."""
import unittest

from src.evaluate import choose_config, evaluate_hits, evidence_checks, quote_in_source_intervals


class EvidenceEvaluationTest(unittest.TestCase):
    def test_quote_must_be_from_the_correct_source_page(self):
        corpus = 'same text.\nsame text.'
        gold = [{'source_id': 'doc1', 'page': 1, 'evidence_quote': 'same text.'}]
        hit = {'text': 'same text.', 'provenance': [{'document_id': 'doc2', 'page': 1, 'start': 11, 'end': 21}]}
        self.assertFalse(evidence_checks(corpus, hit, gold)[0]['hit'])
        hit['provenance'] = [{'document_id': 'doc1', 'page': 2, 'start': 0, 'end': 10}]
        self.assertFalse(evidence_checks(corpus, hit, gold)[0]['hit'])
        hit['provenance'][0]['page'] = 1
        self.assertTrue(evidence_checks(corpus, hit, gold)[0]['hit'])

    def test_prefix_and_body_may_join_only_through_source_whitespace(self):
        refs = [{'document_id': 'doc', 'page': 1, 'start': 0, 'end': 4},
                {'document_id': 'doc', 'page': 1, 'start': 5, 'end': 9}]
        self.assertTrue(quote_in_source_intervals('head body', 'head body', refs, 'doc', 1))
        refs[1].update(start=14, end=18)
        self.assertFalse(quote_in_source_intervals('head omitted! body', 'head body', refs, 'doc', 1))

    def test_evidence_split_across_two_hits_is_not_a_hit3(self):
        corpus = 'alpha beta'
        question = {'id': 'fixture', 'split': 'dev', 'question': 'fixture?', 'expected_answer': 'fixture',
                    'gold_evidence': [{'source_id': 'doc', 'page': 1, 'evidence_quote': corpus}], 'filter': {}}
        hits = [{'text': corpus[start:end], 'provenance': [{'document_id': 'doc', 'page': 1, 'start': start, 'end': end}],
                 'metadata': {}} for start, end in [(0, 6), (6, 10)]]
        result = evaluate_hits(corpus, question, hits, 'A')
        self.assertFalse(result['hit_at_1'])
        self.assertFalse(result['evidence_hit_at_3'])
        self.assertTrue(result['evidence_split_across_top3'])

    def test_documented_alternative_gold_is_accepted(self):
        hit = {'text': 'valid quote', 'provenance': [{'document_id': 'alt', 'page': 3, 'start': 0, 'end': 11}]}
        gold = [{'source_id': 'primary', 'page': 1, 'evidence_quote': 'valid quote'},
                {'source_id': 'alt', 'page': 3, 'evidence_quote': 'valid quote'}]
        self.assertEqual([p['hit'] for p in evidence_checks('valid quote', hit, gold)], [False, True])

    def test_dev_tie_break_uses_predeclared_document_tokens(self):
        rows = [{'strategy': c, 'split': 'dev', 'hit_at_1_rate': 1, 'evidence_hit_at_3_rate': 1} for c in ['A', 'B', 'C']]
        chosen, _ = choose_config(rows, {'A': 300, 'B': 260, 'C': 310})
        self.assertEqual(chosen, 'B')
        rows[0]['split'] = 'test'
        with self.assertRaises(ValueError):
            choose_config(rows, {'A': 300, 'B': 260, 'C': 310})


if __name__ == '__main__':
    unittest.main()
