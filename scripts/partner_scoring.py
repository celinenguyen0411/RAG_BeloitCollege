import csv
from pathlib import Path


def read_scores(path):
    if not Path(path).exists():
        return {}
    with Path(path).open() as f:
        records = list(csv.DictReader(f))
    output = {}
    for row in records:
        key = (row['variant'], row['question_id'])
        if key in output:
            raise ValueError(f'Duplicate score row in {path}: {key}')
        output[key] = row
    return output


def reconcile(rows, destination):
    folder = Path(destination) / 'partner_review'
    mai = read_scores(folder / 'mai_scores.csv')
    parker = read_scores(folder / 'parker_scores.csv')
    consensus = read_scores(folder / 'consensus.csv')
    decisions = []
    for row in rows:
        key = (row['variant'], row['question_id'])
        a, b = mai.get(key, {}), parker.get(key, {})
        decision = {'variant': key[0], 'question_id': key[1], 'correct': None, 'status': 'pending independent scores'}
        for score, name in [(a, 'Mai'), (b, 'Parker')]:
            value = score.get('correct', '').strip()
            if value and value not in ['0', '1']:
                raise ValueError(f'{name} {key}: correct must be 0, 1, or blank')
        ready = (a.get('correct') in ['0', '1'] and b.get('correct') in ['0', '1']
                 and a.get('reviewer', '').strip().lower() == 'mai'
                 and b.get('reviewer', '').strip().lower() == 'parker')
        if ready:
            if a['correct'] == b['correct']:
                decision.update(correct=int(a['correct']), status='independent agreement')
            else:
                settled = consensus.get(key, {})
                people = settled.get('confirmed_by', '').strip().lower()
                if (settled.get('consensus_score') in ['0','1'] and settled.get('resolution_notes', '').strip()
                        and 'mai' in people and 'parker' in people):
                    decision.update(correct=int(settled['consensus_score']), status='disagreement resolved by both partners')
                else:
                    decision['status'] = 'disagreement requires discussion'
        decisions.append(decision)
    return decisions


def correctness_metric(decisions, variant):
    cases = [d for d in decisions if d['variant'] == variant]
    scored = [d for d in cases if d['correct'] is not None]
    complete = len(scored) == len(cases) and bool(cases)
    return {'numerator': sum(d['correct'] for d in scored) if complete else None,
            'denominator': len(cases), 'scored_questions': len(scored),
            'correct_among_scored': sum(d['correct'] for d in scored),
            'status': 'complete' if complete else 'pending partner scoring or reconciliation'}
