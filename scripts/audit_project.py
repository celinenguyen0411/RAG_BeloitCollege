import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from evaluate import validate_gold

def audit():
    issues=[]
    rows=list(csv.DictReader((ROOT/'documents.csv').open()))
    ids={r['id'] for r in rows}
    corpus={p.stem for p in (ROOT/'corpus').glob('*.txt')}
    for doc in sorted(ids-corpus):issues.append(f'Missing corpus document: {doc}')
    for doc in sorted(corpus-ids):issues.append(f'Corpus document absent from document list: {doc}')
    for row in rows:
        url=row['url'].strip()
        path=ROOT/'raw'/(hashlib.sha1(url.encode()).hexdigest()[:16]+('.pdf' if row['kind']=='pdf' else '.html'))
        if not path.exists():issues.append(f'Missing raw snapshot: {row["id"]} -> {path.name}')
    if len(ids) != len(rows):
        issues.append('Duplicate document IDs in documents.csv')
    manifest = ROOT / 'analysis/source_snapshot_manifest.json'
    if not manifest.exists():
        issues.append('Missing source snapshot checksum manifest')
    else:
        for relative, expected in json.loads(manifest.read_text()).items():
            path = ROOT / relative
            if not path.exists():
                issues.append(f'Missing frozen file: {relative}')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                issues.append(f'Frozen snapshot content changed: {relative}')
    validate_gold()
    print(json.dumps({'document_rows':len(rows),'corpus_documents':len(corpus),'issues':issues},indent=2))
    return issues
if __name__=='__main__':sys.exit(bool(audit()))
