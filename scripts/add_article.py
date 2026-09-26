#!/usr/bin/env python3
"""Publish one Markdown article into the static Fourth Frame site.

No third-party packages are needed. Supported Markdown is documented in
ARTICLE-TEMPLATE.md; HTML in submissions is escaped, not interpreted.
"""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://peterdsouza247.github.io/4thframe/"
ARTS = ROOT / "content/articles.json"
HOME = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"
README = ROOT / "README.md"
STORIES = ROOT / "stories"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LOCAL_IMAGE = re.compile(r"(?:\.\./\.\./)?assets/images/[a-zA-Z0-9_./-]+\Z")
REQUIRED = {"title", "slug", "type", "description", "summary", "category", "tags"}
OPTIONAL = {"related", "cover_label", "art", "published"}


def fail(message):
    raise ValueError(message)


def parse_markdown(source):
    if not source.startswith("---\n"):
        fail("Start the file with a --- metadata block (see ARTICLE-TEMPLATE.md)")
    parts = source.split("\n---\n", 1)
    if len(parts) != 2:
        fail("Close the metadata block with a line containing only ---")
    fields = {}
    for line in parts[0].splitlines()[1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            fail(f"Invalid metadata line: {line!r}")
        key, value = (x.strip() for x in line.split(":", 1))
        if key in fields:
            fail(f"Duplicate metadata key: {key}")
        if key not in REQUIRED | OPTIONAL:
            fail(f"Unknown metadata key: {key}")
        if key in {"tags", "related"}:
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                fail(f"{key} must be a JSON array of quoted strings: {exc}")
            if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
                fail(f"{key} must be a JSON array of nonempty strings")
        elif value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                fail(f"Invalid quoted value for {key}: {exc}")
        fields[key] = value
    missing = REQUIRED - fields.keys()
    if missing:
        fail("Missing metadata: " + ", ".join(sorted(missing)))
    for key in REQUIRED - {"tags"}:
        if not isinstance(fields[key], str) or not fields[key].strip():
            fail(f"{key} must be nonempty text")
    if fields["type"] not in {"Long read", "List"}:
        fail('type must be "Long read" or "List"')
    if not SLUG.fullmatch(fields["slug"]):
        fail("slug must contain lowercase letters, numbers and single hyphens")
    if not fields["tags"] or len(fields["tags"]) != len(set(fields["tags"])):
        fail("tags must contain at least one unique tag")
    if fields.get("published"):
        try:
            date.fromisoformat(fields["published"])
        except ValueError:
            fail("published must be YYYY-MM-DD, or omit it until publication")
    if fields.get("art", "") and not re.fullmatch(r"[a-z][a-z0-9-]*", fields["art"]):
        fail("art must be a single CSS class name")
    body = parts[1].strip()
    if not body or not re.search(r"\w", body):
        fail("Write an article body below the metadata block")
    if re.search(r"^#\s", body, flags=re.M):
        fail("The title comes from metadata; start body sections with ##")
    return fields, body


def inline(text):
    """A deliberately small, safe Markdown subset for editorial copy."""
    tokens = []

    def reserve(markup):
        tokens.append(markup)
        return f"\x00{len(tokens)-1}\x00"

    def link(match):
        label, target = match.groups()
        if not (target.startswith("https://") or target.startswith("http://") or target.startswith("../../")):
            fail(f"Use an https:// or ../../ link: {target}")
        return reserve(f'<a href="{escape(target, quote=True)}">{escape(label)}</a>')

    text = re.sub(r"\[([^\]\n]+)\]\(([^\s)]+)\)", link, text)
    text = re.sub(r"`([^`\n]+)`", lambda m: reserve(f"<code>{escape(m.group(1))}</code>"), text)
    text = escape(text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m.group(1))], text)


def render_body(body):
    blocks = re.split(r"\n\s*\n", body)
    result = []
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) == 1 and re.fullmatch(r"#{2,3} .+", lines[0]):
            level, title = lines[0].split(" ", 1)
            result.append(f"<h{len(level)}>{inline(title)}</h{len(level)}>")
        elif len(lines) == 1 and lines[0].startswith("!["):
            image = re.fullmatch(r'!\[([^\]]+)\]\(([^\s)]+) "([^"]+)"\)', lines[0])
            if not image or not LOCAL_IMAGE.fullmatch(image.group(2)) or ".." in Path(image.group(2)).parts:
                fail("Images need ![alt](../../assets/images/file.jpg \"Credit and rights note\") on their own line")
            alt, path, credit = image.groups()
            assert alt and credit
            result.append(f'<figure class="article-figure"><img src="{escape(path, quote=True)}" alt="{escape(alt, quote=True)}" loading="lazy"><figcaption>{escape(credit)}</figcaption></figure>')
        elif all(re.match(r"^\d+\.\s", x) for x in lines):
            items = "".join(f"<li>{inline(re.sub(r'^\d+\.\s+', '', x))}</li>" for x in lines)
            result.append(f"<ol>{items}</ol>")
        elif all(x.startswith("- ") for x in lines):
            result.append("<ul>" + "".join(f"<li>{inline(x[2:])}</li>" for x in lines) + "</ul>")
        elif all(x.startswith("> ") for x in lines):
            result.append("<blockquote><p>" + inline(" ".join(x[2:] for x in lines)) + "</p></blockquote>")
        else:
            if any(x.startswith(("## ", "### ", "![", "- ", "> ")) for x in lines):
                fail("Separate headings, images and lists from paragraphs with a blank line")
            result.append("<p>" + inline(" ".join(lines)) + "</p>")
    return "\n".join(result)


def article_html(meta, body_html, minutes):
    title, slug = meta["title"], meta["slug"]
    h = lambda value: escape(value, quote=True)
    canonical = BASE + f"stories/{slug}/"
    label = meta.get("cover_label") or "FOURTH FRAME"
    band = "list-band" if meta["type"] == "List" else "warcraft-band"
    section = "lists" if meta["type"] == "List" else "long-reads"
    schema = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title,
                         "description": meta["description"], "mainEntityOfPage": canonical}, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#171c28">
  <title>{h(title)} | Fourth Frame</title>
  <meta name="description" content="{h(meta['description'])}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{h(title)}">
  <meta property="og:description" content="{h(meta['description'])}">
  <meta property="og:url" content="{canonical}">
  <link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../assets/style.css">
  <script type="application/ld+json">{schema}</script>
  <script defer src="../../assets/analytics.js"></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="mast"><div class="shell">
    <div class="mast-top"><span>Independent games &amp; culture writing</span><span>Vol. 01 / A different angle on familiar worlds</span></div>
    <div class="mast-row"><a class="wordmark" href="../../" aria-label="Fourth Frame home">Fourth<i>.</i>Frame</a><p class="mast-right">Stories worth revisiting.<br>By Peter D’Souza.</p></div>
    <nav class="nav" aria-label="Sections"><a href="../../#long-reads">Long reads</a><a href="../../#lists">Lists</a><a href="../../search/">Search</a><a href="../../#about">About</a><span>Go deeper ↗</span></nav>
  </div></header>
  <main id="main">
    <header class="article-header wrap"><span class="kicker">{h(meta['category'])}</span><h1>{h(title)}</h1><div class="byline">By Peter D’Souza <span class="article-views" aria-live="off"></span></div></header>
    <div class="article-band {band}" aria-hidden="true"><span>{h(label)}</span></div>
    <div class="article-layout wrap"><aside class="article-aside">Fourth Frame<br>{h(meta['type'])} / {minutes} min</aside><article class="article-body">
{body_html}
<div class="article-end"><a href="../../#{section}">← More {h(meta['type'].lower())}s</a></div>
    </article></div>
  </main>
  <footer class="footer shell"><span>Fourth Frame · Writing by Peter D’Souza</span><a href="#main">Back to top ↑</a></footer>
</body>
</html>
'''


def homepage_card(meta, minutes):
    h = lambda value: escape(value, quote=True)
    slug = meta["slug"]
    if meta["type"] == "List":
        return f'    <div class="list-row"><span class="section-id">00</span><h3><a href="stories/{slug}/">{h(meta["title"])}</a></h3><span class="meta">{h(meta["category"])} ↗</span></div>\n'
    art = meta.get("art", "mass")
    return f'      <article class="story"><div class="story-art {art}" aria-hidden="true"><span class="art-label">{h(meta["category"])} / 00</span></div><div class="story-text"><span class="eyebrow">{h(meta["category"])}</span><h3><a href="stories/{slug}/">{h(meta["title"])}</a></h3><p>{h(meta["summary"])}</p><div class="meta"><span>Peter D’Souza</span><span>{minutes} min</span></div></div></article>\n'


def update_home(home, meta, minutes):
    card = homepage_card(meta, minutes)
    if meta["type"] == "List":
        start = home.index('  <section class="lists shell"')
        end = home.index("  </section>", start)
        section = home[start:end]
        section, n = re.subn(r'(<div class="section-head">.*?</div>\n)', r'\1' + card, section, count=1)
        assert n == 1
        i = iter(range(1, 100))
        section = re.sub(r'(<div class="list-row"><span class="section-id">)\d+(</span>)',
                         lambda m: m[1] + f"{next(i):02d}" + m[2], section)
        return home[:start] + section + home[end:]
    start = home.index('    <div class="stories">\n') + len('    <div class="stories">\n')
    home = home[:start] + card + home[start:]
    i = iter(range(2, 100))
    start = home.index('    <div class="stories">')
    end = home.index('    </div>\n  </section>', start)
    section = home[start:end]
    section = re.sub(r'(<span class="art-label">[^<]+ / )\d+(</span>)',
                     lambda m: m[1] + f"{next(i):02d}" + m[2], section)
    return home[:start] + section + home[end:]


def update_readme(readme, entries):
    lines = [f'- {entry["slug"]}: `stories/{entry["slug"]}/index.html`' for entry in entries]
    start = readme.index('<!-- article-files:start -->')
    end = readme.index('<!-- article-files:end -->') + len('<!-- article-files:end -->')
    return readme[:start] + '<!-- article-files:start -->\n' + '\n'.join(lines) + '\n<!-- article-files:end -->' + readme[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path, help="Article Markdown with metadata header")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print intended changes")
    args = parser.parse_args()
    meta, body = parse_markdown(args.markdown.read_text(encoding="utf-8-sig"))
    entries = json.loads(ARTS.read_text())
    slug = meta["slug"]
    target = STORIES / slug / "index.html"
    if target.exists() or slug in {x["slug"] for x in entries}:
        fail(f"Article already exists: {slug}; edit its HTML and run scripts/build_content.py")
    known = {entry["slug"] for entry in entries}
    related = meta.get("related", [])
    if len(related) != len(set(related)) or not all(x in known for x in related):
        fail("related must contain unique existing article slugs")
    body_html = render_body(body)
    for img in re.findall(r'<img src="([^"]+)"', body_html):
        if not (target.parent / img).exists():
            fail(f"Image does not exist: {img}. Add it and document rights in IMAGE-RIGHTS.md")
    minutes = max(1, round(len(re.findall(r"\b[\w’'-]+\b", body)) / 220))
    page = article_html(meta, body_html, minutes)
    home = update_home(HOME.read_text(), meta, minutes)
    entry = {"slug": slug, "type": meta["type"], "tags": meta["tags"], "related": related}
    if meta.get("published"):
        entry["published"] = meta["published"]
    entries.append(entry)
    readme = update_readme(README.read_text(), entries)
    xml = ET.parse(SITEMAP)
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    url = ET.SubElement(xml.getroot(), f"{{{namespace}}}url")
    ET.SubElement(url, f"{{{namespace}}}loc").text = BASE + f"stories/{slug}/"
    if meta.get("published"):
        ET.SubElement(url, f"{{{namespace}}}lastmod").text = meta["published"]
    if args.dry_run:
        print(f"Would add {target.relative_to(ROOT)} ({minutes} min, {len(meta['tags'])} tags), homepage card, sitemap URL, README entry and search index")
        return
    target.parent.mkdir(parents=True)
    target.write_text(page)
    HOME.write_text(home)
    ARTS.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    README.write_text(readme)
    xml.write(SITEMAP, encoding="unicode", xml_declaration=True)
    with SITEMAP.open("a") as f:
        f.write("\n")
    subprocess.run([sys.executable, str(ROOT / "scripts/build_content.py")], check=True)
    print(f"Added {slug}. Review facts, links and image rights, then commit the changed files.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, AssertionError) as exc:
        sys.exit(f"add_article: {exc}")
