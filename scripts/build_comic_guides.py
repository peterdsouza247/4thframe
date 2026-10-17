#!/usr/bin/env python3
"""Build sourced comics guides and preserve them in every catalogue rebuild."""
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from add_article import article_html, render_body

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://peterdsouza247.github.io/4thframe/'


def block(page, name, markup, marker):
    page = re.sub(r'<!-- ' + name + r':start -->.*?<!-- ' + name + r':end -->', '', page, flags=re.S)
    assert marker in page, f'Missing catalogue marker: {marker}'
    return page.replace(marker, marker + f'<!-- {name}:start -->{markup}<!-- {name}:end -->', 1)


def main():
    guides = json.loads((ROOT / 'content/guides/comic-series.json').read_text())
    assert len({g['slug'] for g in guides}) == len(guides)
    cards, worlds, options, search_rows = [], [], [], []
    for g in guides:
        body = (ROOT / 'content/guides' / (g['slug'] + '.md')).read_text()
        headings = ''.join(f'<th scope="col">{escape(c)}</th>' for c in g['columns'])
        rows = ''.join('<tr>' + ''.join(f'<td>{escape(c)}</td>' for c in row) + '</tr>' for row in g['books'])
        assert all(len(row) == len(g['columns']) for row in g['books'])
        table = f'<div class="comic-table-scroll" role="region" aria-label="Book comparison" tabindex="0"><table class="comic-table"><caption>{escape(g["name"])}: books at a glance</caption><thead><tr>{headings}</tr></thead><tbody>{rows}</tbody></table></div>'
        assert body.count('[BOOKS]') == 1
        markup = render_body(body).replace('<p>[BOOKS]</p>', table)
        meta = dict(g, type='Guide', category='Comics / Reading guide')
        minutes = max(1, round(len(body.split()) / 220))
        page = article_html(meta, markup, minutes)
        page = page.replace('stories/' + g['slug'] + '/', 'guides/' + g['slug'] + '/')
        page = page.replace('article-band warcraft-band', 'article-band ' + g['theme'] + '-band')
        page = page.replace('<h1>', '<a class="guide-back" href="../">← All guides</a><h1>', 1)
        page = page.replace('← More guides', '← All reading and playing guides').replace('href="../../#long-reads">←', 'href="../">←')
        page = page.replace('</head>', '<meta name="author" content="Peter D’Souza"><meta property="og:site_name" content="Fourth Frame"><meta name="twitter:card" content="summary"></head>')
        schema = dict({'@context': 'https://schema.org', '@type': 'Article'}, headline=g['title'], description=g['description'], dateModified=g['reviewed'], mainEntityOfPage=BASE + 'guides/' + g['slug'] + '/', author={'@type': 'Person', 'name': 'Peter D’Souza'}, publisher={'@type': 'Organization', 'name': 'Fourth Frame'}, articleSection='Comics guides')
        page = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>', page, count=1, flags=re.S)
        out = ROOT / 'guides' / g['slug'] / 'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)
        name, slug, description = escape(g['name']), g['slug'], escape(g['summary'])
        terms = escape(' '.join([g['name'], g['search_terms'], *g['tags']]).lower(), quote=True)
        label = 'Comics / Author guide' if g.get('kind') == 'Writer' else 'Comics / Reading guide'
        cards.append(f'<article class="guide-card comic-route" data-universe="{name}" data-medium="comics" data-name="{name.lower()}" data-core-count="{g["steps"]}" data-search="{terms}"><div class="guide-card-top"><span class="guide-universe">{label}</span></div><h3><a href="{slug}/">{name}</a></h3><p>{description}</p><p class="guide-card-summary">Reading routes · collections · optional stories</p><a class="game-guide-link" href="{slug}/">Explore the guide ↗</a></article>')
        worlds.append(f'<article class="world-tile" data-world="{name}" data-medium="comics"><span class="world-orbit" aria-hidden="true"></span><p class="eyebrow">{label}</p><h3>{name}</h3><p>{description}</p><a class="world-primary" href="{slug}/">Explore the guide ↗</a></article>')
        options.append(f'<option value="{name}">{name}</option>')
        # Curated introductory terms only: future guide edits cannot leak twists.
        search_rows.append(dict(title=g['title'], url=f'guides/{slug}/', type='Guide', description=g['description'], tags=['Guides', *g['tags']], body=g['summary'] + ' ' + g['search_terms']))

    catalogue = ROOT / 'guides/index.html'
    page = catalogue.read_text()
    page = block(page, 'comic-guides', ''.join(cards), '<section class="guide-grid" id="guide-grid" aria-label="Character routes">')
    page = block(page, 'comic-worlds', ''.join(worlds), '<section class="world-grid" id="world-grid" aria-label="Choose a world">')
    page = re.sub(r'<!-- comic-options:start -->.*?<!-- comic-options:end -->', '', page, flags=re.S)
    page, count = re.subn(r'(<select id="guide-universe">.*?)(</select>)', lambda m: m[1] + '<!-- comic-options:start -->' + ''.join(options) + '<!-- comic-options:end -->' + m[2], page, count=1, flags=re.S)
    assert count == 1
    count = len(re.findall(r'class="guide-card(?:\s|\")', page))
    page = re.sub(r'(<p class="guide-status"[^>]*>).*?(</p>)', lambda m: m[1] + f'{count} guides. Choose a series, writer or character to begin.' + m[2], page, flags=re.S)
    catalogue.write_text(page)

    index = ROOT / 'search-index.json'
    urls = {row['url'] for row in search_rows}
    entries = [row for row in json.loads(index.read_text()) if row['url'] not in urls]
    index.write_text(json.dumps(entries + search_rows, ensure_ascii=False, indent=2) + '\n')

    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    for g in guides:
        url = BASE + 'guides/' + g['slug'] + '/'
        node = next((n for n in sitemap.getroot() if n.findtext(f'{{{namespace}}}loc') == url), None)
        if node is None:
            node = ET.SubElement(sitemap.getroot(), f'{{{namespace}}}url')
            ET.SubElement(node, f'{{{namespace}}}loc').text = url
        modified = node.find(f'{{{namespace}}}lastmod')
        if modified is None:
            modified = ET.SubElement(node, f'{{{namespace}}}lastmod')
        modified.text = g['reviewed']
    sitemap.write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    print(f'Built {len(guides)} comics guides; updated catalogue, search and sitemap.')


if __name__ == '__main__':
    main()
