#!/usr/bin/env python3
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
DOCS = ROOT / "docs"
CHAPTERS = DOCS / "chapters"

def inline_markup(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s

def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out = []
    para = []

    def flush():
        nonlocal para
        if para:
            out.append("<p>" + inline_markup(" ".join(x.strip() for x in para)) + "</p>")
            para = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped in {"---", "***"}:
            flush()
            out.append("<hr>")
            continue
        if stripped.startswith("### "):
            flush()
            out.append("<h3>" + inline_markup(stripped[4:]) + "</h3>")
            continue
        if stripped.startswith("## "):
            flush()
            out.append("<h2>" + inline_markup(stripped[3:]) + "</h2>")
            continue
        if stripped.startswith("# "):
            flush()
            continue
        para.append(line)
    flush()
    return "\n".join(out)

def chapter_template(ch_id, title, body_html, prev_id, next_id, word_count):
    prev_link = f'../{prev_id}/' if prev_id else '../../#chapters'
    next_link = f'../{next_id}/' if next_id else '../../#chapters'
    prev_label = "Previous" if prev_id else "All chapters"
    next_label = "Next" if next_id else "All chapters"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0e1110">
<meta name="description" content="{html.escape(title)} — Normal Position by Paiea">
<link rel="stylesheet" href="../../styles.css">
<link rel="stylesheet" href="../../reader.css">
<title>{html.escape(title)} — Normal Position</title>
</head>
<body>
<nav class="sitebar"><div class="shell">
<a class="brand" href="../../">Normal Position</a>
<div class="nav"><a href="../../#chapters">Chapters</a></div>
</div></nav>
<main class="reader-shell">
<header class="chapter-head">
<div class="small">CHAPTER {int(ch_id):02d}</div>
<h1>{html.escape(title)}</h1>
<div class="chapter-stats">{word_count:,} words</div>
</header>
<article class="prose">
{body_html}
</article>
<nav class="chapter-nav" aria-label="Chapter navigation">
<a href="{prev_link}">{prev_label}</a>
<a href="{next_link}">{next_label}</a>
</nav>
</main>
<footer class="footer"><div class="shell"><span>Normal Position · by Paiea</span><span>Chapter {int(ch_id):02d}</span></div></footer>
</body>
</html>"""

def main():
    DOCS.mkdir(exist_ok=True)
    CHAPTERS.mkdir(exist_ok=True)

    records = []
    if MANUSCRIPT.exists():
        chapter_dirs = sorted(
            p for p in MANUSCRIPT.iterdir()
            if p.is_dir() and p.name.isdigit() and (p / "current.md").exists()
        )
    else:
        chapter_dirs = []

    parsed = []
    for folder in chapter_dirs:
        raw = (folder / "current.md").read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        title = f"Chapter {int(folder.name)}"
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            body = "\n".join(lines[1:]).strip()
        else:
            body = raw
        words = len(re.findall(r"\b[\w’'-]+\b", body))
        parsed.append((folder.name, title, body, words))

    for i, (ch_id, title, body, words) in enumerate(parsed):
        prev_id = parsed[i-1][0] if i else None
        next_id = parsed[i+1][0] if i+1 < len(parsed) else None
        outdir = CHAPTERS / ch_id
        outdir.mkdir(parents=True, exist_ok=True)
        page = chapter_template(ch_id, title, markdown_to_html(body), prev_id, next_id, words)
        (outdir / "index.html").write_text(page, encoding="utf-8")
        records.append({
            "id": ch_id,
            "title": title,
            "word_count": words,
            "published": True
        })

    manifest = {"title": "Normal Position", "records": records}
    (DOCS / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
