import tempfile,csv,unittest
from pathlib import Path
import rag_pipeline as p
from evaluate import summarize,export_review

class RequiredMetricTests(unittest.TestCase):
    def test_quote_rule_ignores_only_case_and_whitespace(self):
        hits=[('Contact the Office.','d#0',1.)]
        self.assertTrue(p.verify_quote({'source':'d#0','quote':'CONTACT   the office.'},hits))
        self.assertFalse(p.verify_quote({'source':'d#0','quote':'Contact the Oﬃce.'},hits))
        self.assertFalse(p.verify_quote({'source':'d#0','quote':'Contact the office'},[('Contact the “Office”.','d#0',1.)]))
    def test_both_chunk_conditions_cover_the_same_words(self):
        docs=[('a','A',' '.join(f'word{i}' for i in range(1000)))]
        a,_=p.build_chunks(docs,size=250,overlap=50)
        b,_=p.build_chunks(docs,size=200,overlap=50)
        self.assertGreater(len(b),len(a))
        self.assertEqual(set(' '.join(a).split()),set(' '.join(b).split()))
    def test_wrong_refusal_is_counted_even_when_retrieval_failed(self):
        base={'variant':'baseline','answerable':True,'hit':0,'model_answerable':False,'answer':'Missing evidence','evidence':[],'retrieved':[],'api_error':None}
        rows=[base,{**base,'answerable':False,'hit':None}]
        s=summarize(rows)[0]
        self.assertEqual(s['wrong_refusals'],{'numerator':1,'denominator':1})
        self.assertEqual(s['correct_refusals'],{'numerator':1,'denominator':1})
        self.assertIsNone(s['correctness']['numerator'])
    def test_all_quotes_must_match_for_a_quoted_answer(self):
        row={'variant':'baseline','answerable':True,'hit':1,'model_answerable':True,'answer':'x','api_error':None,
             'retrieved':[{'text':'A policy.','source':'a#0','score':1}],
             'evidence':[{'quote':'A policy.','source':'a#0'},{'quote':'Invented.','source':'a#0'}]}
        s=summarize([row])[0]
        self.assertEqual(s['quote_fidelity'],{'numerator':0,'denominator':1})
        self.assertEqual(s['individual_quote_matches'],{'numerator':1,'denominator':2})
    def test_partner_sheets_remain_independent_and_preserve_edits(self):
        row={'variant':'baseline','question_id':'Q01','question':'Question','expected_answer':'Gold','answer':'Generated','answerable':True,'evidence':[]}
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder);export_review([row],destination)
            path=destination/'partner_review/mai_scores.csv'
            with path.open() as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
            self.assertEqual(rows[0]['correct'],'')
            rows[0]['correct']='1';rows[0]['reviewer']='Mai'
            with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
            export_review([row],destination)
            with path.open() as f:self.assertEqual(next(csv.DictReader(f))['correct'],'1')
            with (destination/'partner_review/parker_scores.csv').open() as f:self.assertEqual(next(csv.DictReader(f))['correct'],'')
if __name__=='__main__':unittest.main()
