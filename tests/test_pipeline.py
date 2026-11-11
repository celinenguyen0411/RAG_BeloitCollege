import unittest
import numpy as np
import rag_pipeline as p
from evaluate import validate_gold, retrieval_metrics

class PipelineTests(unittest.TestCase):
    def test_chunk_coverage_overlap(self):
        words = [f'w{i}' for i in range(601)]
        parts = p.chunk(' '.join(words),250,50)
        self.assertEqual(parts[0].split()[-50:],parts[1].split()[:50])
        self.assertEqual(set(' '.join(parts).split()),set(words))
        self.assertTrue(all(len(t.split())<=250 for t in parts))
        with self.assertRaises(ValueError): p.chunk('test',10,10)
    def test_quote_must_match_claimed_source(self):
        hits=[('Office policy applies.','doc#0',0.9)]
        self.assertTrue(p.verify_quote({'quote':'Office policy','source':'doc#0'},hits))
        self.assertFalse(p.verify_quote({'quote':'Office policy','source':'fake#0'},hits))
        self.assertFalse(p.verify_quote({'quote':'Free housing','source':'doc#0'},hits))
    def test_id_selection_prevents_corrupted_quotes(self):
        hits=[('Contact the Residence Life Oﬃce.','doc#0',0.9)]
        out=p.attach_evidence({'answer':'Contact Residence Life.','answerable':True,'evidence_ids':['doc#0:s0']},hits)
        self.assertTrue(out['quote_verified'])
        self.assertEqual(out['evidence'][0]['quote'],hits[0][0])
        bad=p.attach_evidence({'answer':'x','answerable':True,'evidence_ids':['fake']},hits)
        self.assertFalse(bad['answerable'])
        refused=p.attach_evidence({'answer':'No personal data.','answerable':False,'evidence_ids':[]},hits)
        self.assertEqual(refused['citation_status'],'not_applicable')
    def test_gold_and_corpus(self):
        qs=validate_gold();self.assertEqual(len(qs),25)
        self.assertEqual(sum(not q['answerable'] for q in qs),4)
        texts,sources=p.build_chunks(p.load_documents())
        self.assertGreaterEqual(len(texts),150)
        self.assertEqual(len(texts),len(sources))
    def test_multi_source_recall(self):
        q={'question_id':'Q20','answerable':True,'relevant_doc_ids':['a','b'],
           'expected_evidence':[{'doc_id':'a','quote':'A sentence.'},{'doc_id':'b','quote':'B sentence.'}]}
        m=retrieval_metrics(q,[('A sentence.','a#0',1.0),('A sentence.','a#1',0.9)])
        self.assertEqual(m['document_recall'],0.5)
        self.assertEqual(m['evidence_coverage'],0.5)
    def test_cosine_and_fingerprint(self):
        matrix=np.array([[1.,0.],[0.,1.]])
        self.assertEqual(p.cosine_top_k(matrix,np.array([1.,0.]),1)[0][0],0)
        self.assertNotEqual(p.fingerprint(['a']),p.fingerprint(['b']))

if __name__=='__main__': unittest.main()
