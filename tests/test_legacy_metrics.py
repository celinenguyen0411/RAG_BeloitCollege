import json,csv,tempfile,unittest
from pathlib import Path
from evaluate_metrics import verify_source_quote,load_and_prepare_eval

class LegacyMetricTests(unittest.TestCase):
    def record(self):
        return {'source':'doc#0','quote':'Real policy.', 'retrieved':[['doc#0',0.9],['other#0',0.8]],
                'prompt':'PASSAGES:\n[doc#0]\nReal policy.\n\n[other#0]\nOther text.\n\nQUESTION: Real policy.'}
    def test_case_and_spaces_match_only_claimed_source(self):
        row=self.record();row['quote']='REAL   policy.'
        self.assertTrue(verify_source_quote(row))
        row['source']='other#0';self.assertFalse(verify_source_quote(row))
    def test_question_text_and_old_verified_flag_do_not_count(self):
        row=self.record();row['quote']='Invented question text';row['quote_verified']=True
        row['prompt']+=' Invented question text'
        self.assertFalse(verify_source_quote(row))
    def test_existing_score_is_kept(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=self.record();out.update(question='A question?',expected_doc='doc')
            (root/'results.json').write_text(json.dumps([out]))
            (root/'grades.csv').write_text('question,correct\nA question?,1\n')
            rows=load_and_prepare_eval(root/'results.json',root/'grades.csv')
            self.assertEqual(rows[0]['correct'],'1')
            self.assertEqual((root/'grades.csv').read_text(),'question,correct\nA question?,1\n')
if __name__=='__main__':unittest.main()
