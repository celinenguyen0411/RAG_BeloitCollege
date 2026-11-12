"""Report the older single-run evaluation without changing existing grades.

The final chunk-size comparison uses scripts/build_reports.py instead.
Use --write-csv only when you want to refresh the older grading sheet.
"""
import argparse
import csv
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent


def norm(s):
    return ' '.join((s or '').lower().split())


def verify_source_quote(out):
    """Search only the claimed retrieved passage, never the question or whole prompt."""
    quote = norm(out.get('quote'))
    source = (out.get('source') or '').strip().strip('[]')
    retrieved = {str(item[0]) for item in out.get('retrieved', [])[:3]}
    if not quote or not source or source not in retrieved:
        return False
    passages = dict(re.findall(
        r'^\[([^\]\n]+)\]\s*\n(.*?)(?=^\[[^\]\n]+\]\s*\n|\n\nQUESTION:|\Z)',
        out.get('prompt', ''), flags=re.M | re.S))
    return source in passages and quote in norm(passages[source])


def load_and_prepare_eval(results_path=None, grades_path=None):
    results_path = Path(results_path) if results_path else ROOT / 'eval_results.json'
    grades_path = Path(grades_path) if grades_path else ROOT / 'eval_for_grading.csv'
    existing = {}
    if grades_path.exists():
        with grades_path.open(newline='') as f:
            existing = {r['question']: r.get('correct', '') for r in csv.DictReader(f)}
    rows = []
    for out in json.loads(results_path.read_text(encoding='utf-8')):
        expected_doc = out.get('expected_doc', '')
        retrieved = [item[0].split('#')[0].replace('.txt', '').strip()
                     for item in out.get('retrieved', [])[:3]]
        expected = [d.strip() for d in expected_doc.split(',') if d.strip()]
        rows.append({'question': out['question'], 'expected_doc': expected_doc,
                     'retrieved_top3': ', '.join(retrieved),
                     'hit': int(any(d in retrieved for d in expected)),
                     'quote_found': int(verify_source_quote(out)),
                     'refused': int(out.get('answerable') is False),
                     'answerable': out.get('answerable'), 'answer': out.get('answer', ''),
                     'quote': out.get('quote', ''),
                     'correct': existing.get(out['question'], '')})
    return rows


def print_metrics(rows):
    answerable = [r for r in rows if r['expected_doc']]
    unavailable = [r for r in rows if not r['expected_doc']]
    quoted = [r for r in rows if r['quote']]
    print('Older single-run evaluation; not the final chunk-size comparison.')
    print('Hit rate:', sum(r['hit'] for r in answerable), 'of', len(answerable))
    print('Quote fidelity (quoted answers):', sum(r['quote_found'] for r in quoted), 'of', len(quoted))
    print('Verified-quote answers (all questions):', sum(r['quote_found'] for r in rows), 'of', len(rows))
    print('Correct refusals:', sum(r['refused'] for r in unavailable), 'of', len(unavailable))
    print('Wrong refusals:', sum(r['refused'] for r in answerable), 'of', len(answerable))
    scored = [r for r in rows if str(r['correct']).strip() in ['0', '1']]
    if len(scored) == len(rows):
        print('Correctness (existing older scores):', sum(int(r['correct']) for r in scored), 'of', len(rows))
    else:
        print('Correctness pending:', len(scored), 'of', len(rows), 'scored')
    print('The final comparison still requires separate Mai/Parker scores and reconciliation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-csv', action='store_true', help='refresh the older sheet, preserving matching scores')
    args = parser.parse_args()
    rows = load_and_prepare_eval()
    print_metrics(rows)
    if args.write_csv and rows:
        with (ROOT / 'eval_for_grading.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        print('Updated older grading sheet; matching existing scores were preserved.')
