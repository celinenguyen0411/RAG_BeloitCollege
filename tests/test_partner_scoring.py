import csv,tempfile,unittest
from pathlib import Path
from scripts.partner_scoring import reconcile,correctness_metric

class PartnerScoringTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'partner_review').mkdir()
        self.rows=[{'variant':'baseline','question_id':'Q01'}]
    def tearDown(self):self.tmp.cleanup()
    def write(self,name,data):
        path=self.root/'partner_review'/name
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data));w.writeheader();w.writerow(data)
    def score(self,name,value,reviewer):
        self.write(name+'_scores.csv',dict(variant='baseline',question_id='Q01',correct=value,reviewer=reviewer))
    def test_single_or_ai_score_cannot_finalize_correctness(self):
        self.score('mai','1','Mai')
        self.assertIsNone(reconcile(self.rows,self.root)[0]['correct'])
        self.score('parker','1','Codex')
        self.assertIsNone(reconcile(self.rows,self.root)[0]['correct'])
    def test_independent_agreement(self):
        self.score('mai','1','Mai');self.score('parker','1','Parker')
        metric=correctness_metric(reconcile(self.rows,self.root),'baseline')
        self.assertEqual(metric['numerator'],1);self.assertEqual(metric['denominator'],1)
    def test_disagreement_needs_score_notes_and_both_names(self):
        self.score('mai','1','Mai');self.score('parker','0','Parker')
        self.assertIsNone(reconcile(self.rows,self.root)[0]['correct'])
        self.write('consensus.csv',dict(variant='baseline',question_id='Q01',consensus_score='0',resolution_notes='Missing required condition.',confirmed_by='Mai and Parker'))
        self.assertEqual(reconcile(self.rows,self.root)[0]['correct'],0)
    def test_partial_scores_do_not_become_final_accuracy(self):
        decisions=[{'variant':'baseline','correct':1},{'variant':'baseline','correct':None}]
        metric=correctness_metric(decisions,'baseline')
        self.assertIsNone(metric['numerator']);self.assertEqual(metric['scored_questions'],1)
if __name__=='__main__':unittest.main()
