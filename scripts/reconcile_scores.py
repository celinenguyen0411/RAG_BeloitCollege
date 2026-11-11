import json,sys
from pathlib import Path
from partner_scoring import reconcile,correctness_metric
ROOT=Path(__file__).resolve().parents[1]
run=ROOT/(ROOT/'analysis/final_vertex_run.txt').read_text().strip()
if len(sys.argv)>1:run=Path(sys.argv[1]).resolve()
rows=json.loads((run/'results.json').read_text())
decisions=reconcile(rows,run)
(run/'correctness_reconciliation.json').write_text(json.dumps(decisions,indent=2)+'\n')
metrics=[{'variant':v,**correctness_metric(decisions,v)} for v in ['baseline','candidate']]
print(json.dumps(metrics,indent=2))
if any(d['correct'] is None for d in decisions):
    print('Correctness is not final. Complete both independent sheets and resolve disagreements.')
    sys.exit(1)
