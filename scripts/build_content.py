#!/usr/bin/env python3
"""Refresh article metadata, topic links and the committed static search index."""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "content/articles.json").read_text())
BY_SLUG = {entry["slug"]: entry for entry in CONFIG}
assert len(BY_SLUG) == len(CONFIG), "Duplicate article slug"


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(markup):
    parser = PlainText()
    parser.feed(markup)
    return " ".join(" ".join(parser.parts).split())


def one(pattern, html, slug):
    match = re.search(pattern, html, flags=re.S | re.I)
    assert match, f"Missing HTML field in {slug}: {pattern}"
    return match.group(1)


def page_details(slug):
    path = ROOT / "stories" / slug / "index.html"
    html = path.read_text()
    title = plain(one(r"<h1[^>]*>(.*?)</h1>", html, slug))
    description = unescape(one(r'<meta name="description" content="([^"]+)"', html, slug))
    canonical = one(r'<link rel="canonical" href="([^"]+)"', html, slug)
    assert canonical.endswith(f"/stories/{slug}/")
    return path, html, title, description, canonical


details = {entry["slug"]: page_details(entry["slug"]) for entry in CONFIG}
search_index = []

for entry in CONFIG:
    slug = entry["slug"]
    path, html, title, description, canonical = details[slug]
    assert len(entry["tags"]) == len(set(entry["tags"]))
    assert all(other in BY_SLUG and other != slug for other in entry["related"])

    # Regenerate this owned block so the script can be run again after copy edits.
    html = re.sub(r"\s*<!-- site-meta:start -->.*?<!-- site-meta:end -->\s*(?=</head>)", "", html, flags=re.S)
    extras = [
        '<!-- site-meta:start -->',
        '<meta name="author" content="Peter D’Souza">',
        '<meta property="og:site_name" content="Fourth Frame">',
        '<meta property="og:locale" content="en_GB">',
        '<meta name="twitter:card" content="summary">',
        f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
        f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
    ]
    extras += [f'<meta property="article:tag" content="{escape(tag, quote=True)}">' for tag in entry["tags"]]
    if entry.get("published"):
        extras.append(f'<meta property="article:published_time" content="{entry["published"]}">')
    extras.append('<!-- site-meta:end -->')
    html = html.replace("</head>", "\n  " + "\n  ".join(extras) + "\n</head>", 1)

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "inLanguage": "en",
        "articleSection": entry["type"],
        "keywords": entry["tags"],
        "mainEntityOfPage": canonical,
        "author": {"@type": "Person", "name": "Peter D’Souza", "url": "https://peterdsouza247.github.io/4thframe/#about"},
        "publisher": {"@type": "Organization", "name": "Fourth Frame", "url": "https://peterdsouza247.github.io/4thframe/"}
    }
    if entry.get("published"):
        schema["datePublished"] = entry["published"]
    replacement = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>"
    html, count = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda _: replacement, html, count=1, flags=re.S)
    assert count == 1, f"Missing Article JSON-LD: {slug}"

    if '<a href="../../search/">Search</a>' not in html:
        html = html.replace('<a href="../../#about">About</a>', '<a href="../../search/">Search</a><a href="../../#about">About</a>', 1)
    html = re.sub(r"\s*<!-- topics:start -->.*?<!-- topics:end -->\s*(?=<div class=\"article-end\">)", "", html, flags=re.S)
    chips = " ".join(
        f'<a href="../../search/?tag={quote(tag)}">{escape(tag)}</a>' for tag in entry["tags"]
    )
    links = "".join(
        f'<li><a href="../../stories/{other}/">{escape(details[other][2])}</a></li>'
        for other in entry["related"]
    )
    topics = f"""<!-- topics:start -->
<div class="article-tags" aria-label="Topics"><span>Explore topics</span>{chips}</div>
<aside class="related-stories" aria-label="Related stories"><h2>Keep reading</h2><ul>{links}</ul></aside>
<!-- topics:end -->
"""
    assert '<div class="article-end">' in html, slug
    html = html.replace('<div class="article-end">', "\n" + topics + '<div class="article-end">', 1)
    path.write_text(html)

    body_markup = one(r'<article class="article-body">(.*?)<!-- topics:start -->', html, slug)
    search_index.append({
        "title": title,
        "url": f"stories/{slug}/",
        "type": entry["type"],
        "description": description,
        "tags": entry["tags"],
        "body": plain(body_markup)
    })

(ROOT / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, indent=2) + "\n")
print(f"Updated {len(search_index)} article pages and search-index.json")
