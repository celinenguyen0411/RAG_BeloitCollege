#!/usr/bin/env python3
"""
DSDA 310 - Project 2 corpus ingestion.

Turns a list of Beloit web pages and PDF sections into one clean text file per
DOCUMENT, with a header saying where each one came from.

    pip install requests trafilatura pypdf
    python beloit_ingest.py --check     # fetch, extract, show a sample of each
    python beloit_ingest.py             # fetch and write corpus/

ONE ROW IN documents.csv IS ONE DOCUMENT, NOT ONE FILE.
A document is one thing retrieval can return: a single policy, a single program
description, a single procedure. The student handbook is one PDF and roughly forty
documents. Four source files can easily be forty rows. A pair that ingests the
handbook as a single row builds a system where every question returns the whole
handbook.

Raw downloads are cached in raw/. After the first run everyone on your team works
from that snapshot, so a page edited mid-project cannot silently change your results.
Commit raw/ and corpus/ to your repository.

documents.csv columns:
    id      short slug, becomes the filename, e.g. handbook-academic-honesty
    kind    html | pdf
    url     the address to fetch, or a local path to a file you downloaded by hand
    title   human-readable title
    pages   PDF only, e.g. 41-58 . Blank means the whole file, which is almost
            never what you want for a long PDF.

------------------------------------------------------------------------------
NOTE: text_from_pdf() is now written. It extracts the requested pages and nothing
else. It does NOT remove running headers, page numbers or repeated footers - that
text is still in what you get back, and finding it is your job. Run --check and
read every extraction.
------------------------------------------------------------------------------
"""
import argparse, csv, datetime, hashlib, io, os, re, sys, time
from pathlib import Path

RAW = Path("raw")
OUT = Path("corpus")
UA = "DSDA310-coursework/1.0 (Beloit College class project; contact your instructor)"
DELAY = 1.0

# A PDF longer than this with a blank pages column is almost certainly several
# documents being ingested as one. Warn loudly rather than fail, so a short
# printed-to-PDF web page still works with pages left blank.
WHOLE_FILE_WARN_PAGES = 5


def need(mod, pipname=None):
    try:
        return __import__(mod)
    except ImportError:
        sys.exit(f"Missing package '{mod}'. Run:  pip install {pipname or mod}")


def fetch(url, kind):
    """Download once, then reuse the cached copy in raw/."""
    if not re.match(r"^https?://", url):
        p = Path(url)
        if not p.exists():
            raise FileNotFoundError(f"local file not found: {url}")
        return p.read_bytes(), False
    requests = need("requests")
    ext = ".pdf" if kind == "pdf" else ".html"
    cached = RAW / (hashlib.sha1(url.encode()).hexdigest()[:16] + ext)
    if cached.exists():
        return cached.read_bytes(), True
    RAW.mkdir(exist_ok=True)
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    cached.write_bytes(r.content)
    time.sleep(DELAY)
    return r.content, False


def text_from_html(raw, url):
    """Pulls the main content out of a web page and leaves the navigation,
    the header and the footer behind."""
    trafilatura = need("trafilatura")
    html = raw.decode("utf-8", errors="replace")
    txt = trafilatura.extract(
        html, url=url, favor_precision=True,
        include_comments=False, include_tables=True, no_fallback=False,
    )
    if not txt:
        raise ValueError("no main content extracted - the page may be mostly navigation, "
                         "or JavaScript-rendered. Save it as a PDF from the browser and "
                         "use kind=pdf instead.")
    return txt


def parse_pages(pages, n):
    """Turn the pages column into 1-based inclusive (first, last).

    "" -> the whole file.  "7" -> page 7.  "41-58" -> pages 41 to 58.

    A range that runs past the end is clamped to the last page and reported, so
    an off-by-one in documents.csv shows up in the run output instead of silently
    producing a short document. A start page outside the file is an error.
    """
    pages = (pages or "").strip()
    if not pages:
        return 1, n, (f"pages column is blank, taking all {n} pages as ONE document"
                      if n > WHOLE_FILE_WARN_PAGES else None)
    m = re.fullmatch(r"(\d+)\s*(?:-\s*(\d+))?", pages)
    if not m:
        raise ValueError(f"pages column {pages!r} is not a page or a range like 41-58")
    first = int(m.group(1))
    last = int(m.group(2)) if m.group(2) else first
    if last < first:
        raise ValueError(f"pages {pages!r} ends before it starts")
    if first < 1 or first > n:
        raise ValueError(f"pages {pages!r} starts outside this file, which has {n} pages")
    note = None
    if last > n:
        note = f"pages {pages} runs past the end; clamped to {first}-{n}"
        last = n
    return first, last, note


def unwrap(body):
    """Rejoin text that came out of the PDF one word per line.

    Some PDFs - the Beloit student handbook among them - give back every word on
    its own line, so the extracted text looks like a list of words rather than
    prose. Left alone, tidy() turns each of those line breaks into a paragraph
    break and anything that splits on blank lines produces one-word chunks.

    The test is the length of the lines themselves: if most of them are shorter
    than a short phrase, the line breaks are not real and the lines are joined.
    A document whose lines are genuinely short, such as a list of one-word items,
    is joined too; that is the cost of the rule.
    """
    lines = [ln.strip() for ln in body.split("\n")]
    lines = [ln for ln in lines if ln]
    if not lines:
        return body
    short = sum(1 for ln in lines if len(ln) <= 20)
    if short / len(lines) < 0.6:
        return body
    return " ".join(lines)


def text_from_pdf(raw, pages):
    """Return the text of the requested pages of a PDF.

    Pages are marked with a [page N] line. Those markers are part of the text you
    chunk and embed, so decide deliberately whether to keep them: they tell you
    where an answer came from, and they also put a line of non-document text inside
    whatever chunk straddles the break. Set PAGE_MARKERS to False to drop them.
    """
    PdfReader = need("pypdf").PdfReader
    reader = PdfReader(io.BytesIO(raw))
    n = len(reader.pages)
    first, last, note = parse_pages(pages, n)
    if note:
        print(f"  note  {note}")
    PAGE_MARKERS = True
    out = []
    empty = []
    for i in range(first - 1, last):
        body = unwrap((reader.pages[i].extract_text() or "").strip())
        if not body:
            empty.append(i + 1)
            continue
        out.append(f"[page {i + 1}]\n{body}" if PAGE_MARKERS else body)
    if empty:
        print(f"  note  no extractable text on page(s) {', '.join(map(str, empty))} - "
              f"scanned images? check the original")
    if not out:
        raise ValueError(f"pages {first}-{last} produced no text at all - this PDF may be "
                         f"scanned images rather than text")
    return "\n\n".join(out)


def tidy(t):
    t = t.replace("\r\n", "\n").replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def tidy(t):
    if not t:
        return ""

    # 1. First convert non-breaking spaces (\xa0) to standard spaces so exact matching works
    t = t.replace("\xa0", " ")

    # 2. Strip out all known header and TOC variations
    phrases_to_remove = [
        "2025-2027 BELOIT COLLEGE CATALOG",
        "BELOIT COLLEGE CATALOG 2025-2027",
        "2024-2026 BELOIT COLLEGE CATALOG",
        "BELOIT COLLEGE CATALOG 2024-2026",
        "Click here to return to Table of Contents ii.",
        "Click here to return to Table of Contents i.",
        "Click here to return to Table of Contents",
    ]
    for phrase in phrases_to_remove:
        t = t.replace(phrase, "")

    # 3. Professor's original whitespace cleanup
    t = t.replace("\r\n", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--documents", "--sources", dest="documents", default="documents.csv")
    ap.add_argument("--check", action="store_true",
                    help="print a sample of each document instead of writing corpus/")
    ap.add_argument("--sample", type=int, default=400, help="characters to show with --check")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.documents, newline="", encoding="utf-8-sig")))
    if not rows:
        sys.exit(f"{args.documents} has no rows.")
    missing = {"id", "kind", "url", "title"} - set(rows[0])
    if missing:
        sys.exit(f"{args.documents} is missing column(s): {', '.join(sorted(missing))}")

    if not args.check:
        OUT.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    manifest, failures = [], []

    for r in rows:
        rid = (r["id"] or "").strip()
        kind = (r["kind"] or "").strip().lower()
        url = (r["url"] or "").strip()
        title = (r["title"] or "").strip()
        pages = (r.get("pages") or "").strip()
        if not rid or not url:
            continue
        try:
            raw, cached = fetch(url, kind)
            body = text_from_pdf(raw, pages) if kind == "pdf" else text_from_html(raw, url)
            body = tidy(body)
        except Exception as e:
            failures.append((rid, f"{type(e).__name__}: {e}"))
            print(f"  FAIL  {rid}: {e}")
            continue

        if len(body) < 250:
            print(f"  SHORT {rid}: only {len(body)} characters - open it and check "
                  f"nothing was lost")
        words = len(body.split())
        head = (f"id: {rid}\ntitle: {title}\nsource: {url}\n"
                f"kind: {kind}{f' pages {pages}' if pages else ''}\nretrieved: {today}\n"
                + "-" * 60 + "\n")
        if args.check:
            print(f"\n=== {rid}  ({words} words{', cached' if cached else ''})")
            print(body[:args.sample].replace("\n", " ") + ("..." if len(body) > args.sample else ""))
        else:
            (OUT / f"{rid}.txt").write_text(head + body, encoding="utf-8")
            print(f"  ok    {rid}  {words} words")
        manifest.append({"id": rid, "title": title, "source": url, "kind": kind,
                         "pages": pages, "words": words, "chars": len(body),
                         "retrieved": today})

    if not args.check and manifest:
        with open(OUT / "manifest.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(manifest[0]))
            w.writeheader()
            w.writerows(manifest)

    print(f"\n{len(manifest)} document(s) processed, {len(failures)} failed.")
    if manifest:
        ws = sorted(m["words"] for m in manifest)
        print(f"total {sum(ws):,} words, median document {ws[len(ws)//2]:,} words")
        big = [m["id"] for m in manifest if m["words"] > 4000]
        if big:
            print(f"  long document(s), probably several documents in one row: "
                  f"{', '.join(big)}")
    for rid, msg in failures:
        print(f"  still failing: {rid}  {msg}")
    if failures:
        print("\nFor a page that will not extract: open it in the browser, print to PDF, "
              "put the file next to this script, and change that row to kind=pdf with "
              "the filename as url.")
    if manifest and not args.check:
        print("\nNow run --check and READ the output. Every document, not a sample of "
              "them. You are looking for anything in the text that a reader of the "
              "original would not call part of the document.")


if __name__ == "__main__":
    main()
