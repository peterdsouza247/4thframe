#!/usr/bin/env python3
"""Apply edits from export_articles.py; preview with --dry-run. Python stdlib only."""
import argparse
from datetime import date
import difflib
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

import export_articles as exchange
from add_article import render_body, parse_markdown


def read_bundle(content):
    header = re.search(r'^<!-- fourth-frame:bundle (\{.*\}) -->$', content, re.M)
    if not header:
        raise ValueError('Missing bundle header; use export_articles.py to create this file')
    manifest = json.loads(header[1])
    if manifest.get('version') != 1 or not isinstance(manifest.get('slugs'), list):
        raise ValueError('Unsupported bundle format')
    result = {}
    matches = list(exchange.START.finditer(content))
    for i, match in enumerate(matches):
        marker = json.loads(match[1])
        slug = marker.get('slug', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in result:
            raise ValueError(f'Invalid or duplicate article slug: {slug}')
        if any(not re.fullmatch(r'[0-9a-f]{64}', marker.get(k, '')) for k in ('sha256', 'edit_sha256')):
            raise ValueError(f'Invalid snapshot marker: {slug}')
        section = content[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(content)].strip()
        if not section.endswith(exchange.END) or section.count(exchange.END) != 1:
            raise ValueError(f'Missing end marker or unexpected content after {slug}')
        section = section[:-len(exchange.END)].strip()
        if not section.startswith('---\n') or '\n---\n' not in section:
            raise ValueError(f'Missing article field block: {slug}')
        meta, body = section[4:].split('\n---\n', 1)
        fields = {}
        for line in meta.splitlines():
            if ':' not in line:
                raise ValueError(f'Invalid field in {slug}: {line}')
            key, value = line.split(':', 1)
            if key not in exchange.FIELDS or key in fields:
                raise ValueError(f'Unknown or duplicate field in {slug}: {key}')
            fields[key] = json.loads(value)
        if set(fields) != set(exchange.FIELDS) or any(not isinstance(v, str) for v in fields.values()):
            raise ValueError(f'{slug}: title, description, summary and deck must be quoted strings')
        if any(not fields[k].strip() for k in ('title', 'description', 'summary')):
            raise ValueError(f'{slug}: title, description and summary cannot be empty')
        if not body.strip() or re.search(r'^#\s', body, re.M):
            raise ValueError(f'{slug}: keep an article body; use ## or ### headings inside it')
        result[slug] = dict(marker=marker, fields=fields, body=body.strip())
    expected = manifest['slugs']
    if len(expected) != len(set(expected)) or set(expected) != set(result):
        raise ValueError('Missing, renamed or additional article sections; export again instead of deleting markers')
    return result


def source_text(meta, body):
    lines = ['---'] + [key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in meta.items()]
    return '\n'.join(lines + ['---', '', body, ''])


def reading_minutes(body):
    body = re.sub(r'^\[\^\d+\]: .+$', '', body, flags=re.M)
    body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)
    return max(1, round(len(re.findall(r"\b[\w’'-]+\b", body)) / 220))


def replace_one(pattern, replacement, markup, label):
    markup, count = re.subn(pattern, replacement, markup, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Could not locate ' + label)
    return markup


def update_home(home, slug, old, new, minutes):
    path = re.escape(f'stories/{slug}/')
    patterns = [rf'<article class="(?:story|journal-entry)">(?:(?!</article>).)*?href="{path}"(?:(?!</article>).)*?</article>',
                rf'<div class="list-row">(?:(?!</div>).)*?href="{path}"(?:(?!</div>).)*?</div>',
                rf'<div class="feature-copy">(?:(?!</div>).)*?href="{path}"(?:(?!</div>).)*?</div>']
    for pattern in patterns:
        match = re.search(pattern, home, re.S)
        if not match:
            continue
        card = match[0]
        if old['title'] != new['title']:
            heading = 'h2' if 'class="feature-copy"' in card else 'h3'
            if heading == 'h2':
                card = replace_one(r'(<h2\b[^>]*>).*?(</h2>)', lambda m:m[1] + escape(new['title']) + m[2], card, slug + ' homepage title')
            else:
                card = replace_one(r'(<h3\b[^>]*>\s*<a\b[^>]*>).*?(</a>\s*</h3>)', lambda m:m[1] + escape(new['title']) + m[2], card, slug + ' homepage title')
        if old['summary'] != new['summary'] and '<p>' in card:
            card = replace_one(r'<p>.*?</p>', lambda _: '<p>' + escape(new['summary']) + '</p>', card, slug + ' summary')
        card = re.sub(r'\b\d+ min\b', str(minutes) + ' min', card)
        return home[:match.start()] + card + home[match.end():]
    raise ValueError(f'No homepage card found for {slug}')


def prepare_page(data, fields, rendered, minutes):
    page = exchange.BODY.sub(lambda m: m[1] + '\n' + rendered + '\n', data['page'], count=1)
    page = replace_one(r'(<h1\b[^>]*>).*?(</h1>)', lambda m:m[1] + escape(fields['title']) + m[2], page, 'H1')
    page = replace_one(r'<title>.*?</title>', lambda _: '<title>' + escape(fields['title']) + ' | Fourth Frame</title>', page, 'page title')
    for key, value in [('description', fields['description']), ('og:title', fields['title']), ('og:description', fields['description'])]:
        page = replace_one(r'(<meta (?:name|property)="' + key + r'" content=")[^"]*(")', lambda m:m[1] + escape(value, quote=True) + m[2], page, key)
    deck = '<p class="article-deck">' + escape(fields['deck']) + '</p>' if fields['deck'] else ''
    if 'class="article-deck"' in page:
        page = replace_one(r'<p class="article-deck">.*?</p>', lambda _:deck, page, 'article deck')
    elif deck:
        page = replace_one(r'(</h1>)', lambda m:m[1] + deck, page, 'article deck position')
    page = re.sub(r'(<aside class="article-aside">).*?(</aside>)',
                  lambda m:m[1] + 'Fourth Frame<br>' + data['type'] + ' / ' + str(minutes) + ' min' + m[2], page, count=1, flags=re.S)
    return page


def validate_links(root, slug, markup):
    tree = exchange.Tree(markup).root
    ids = set()
    links = []
    def walk(node):
        if isinstance(node, str):
            return
        if 'id' in node.attrs:
            if node.attrs['id'] in ids:
                raise ValueError(f'{slug}: duplicate anchor {node.attrs["id"]}')
            ids.add(node.attrs['id'])
        for key in ('href', 'src'):
            if key in node.attrs:
                links.append(node.attrs[key])
        for c in node.children:
            walk(c)
    walk(tree)
    parent = root / 'stories' / slug
    for link in links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = (parent / unquote(url.path)).resolve() if url.path else parent / 'index.html'
        if not target.is_relative_to(root):
            raise ValueError(f'{slug}: link leaves repository: {link}')
        if target.is_dir():
            target /= 'index.html'
        if not target.exists():
            raise ValueError(f'{slug}: missing local link or image: {link}')
        if url.fragment:
            target_ids = ids if target == parent / 'index.html' else set(re.findall(r'\bid="([^"]+)"', target.read_text(encoding='utf-8')))
            if unquote(url.fragment) not in target_ids:
                raise ValueError(f'{slug}: missing anchor: {link}')


def apply_bundle(root, path, dry_run=False):
    root, path = root.resolve(), path.resolve()
    incoming = read_bundle(path.read_text(encoding='utf-8-sig'))
    entries = {e['slug']:e for e in exchange.inventory(root)}
    changes = {}
    for slug, article in incoming.items():
        if slug not in entries:
            raise ValueError(f'Unknown article {slug}; this tool updates existing articles only')
        if exchange.edit_digest(article['fields'], article['body']) == article['marker']['edit_sha256']:
            continue
        live = exchange.current(root, entries[slug])
        if live['fingerprint'] != article['marker']['sha256']:
            raise ValueError(f'{slug} changed since export. Save your edits separately, export a fresh file and reapply them.')
        rendered = render_body(article['body'])
        changes[slug] = dict(article=article, live=live, rendered=rendered)
    if not changes:
        print('No article changes. Nothing written.')
        return []

    # Build and validate in an isolated copy; errors cannot leave a half-updated site.
    with tempfile.TemporaryDirectory(prefix='fourth-frame-import-') as tmp:
        stage = Path(tmp) / 'site'
        shutil.copytree(root, stage, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        home = (stage / 'index.html').read_text(encoding='utf-8')
        for slug, change in changes.items():
            article, live = change['article'], change['live']
            minutes = reading_minutes(article['body'])
            live['type'] = entries[slug]['type']
            page = prepare_page(live, article['fields'], change['rendered'], minutes)
            (stage / 'stories' / slug / 'index.html').write_text(page, encoding='utf-8')
            home = update_home(home, slug, live['fields'], article['fields'], minutes)
            meta = dict(live['source_meta'])
            meta.update(slug=slug, type=entries[slug]['type'], tags=entries[slug]['tags'],
                        related=entries[slug]['related'], category=exchange.text(exchange.Tree(page).root.find('span', 'kicker')),
                        **article['fields'])
            if entries[slug].get('published'):
                meta['published'] = entries[slug]['published']
            else:
                meta.pop('published', None)
            if entries[slug]['type'] == 'Long read' and re.search(r'class="article-end">\s*<a href="../../#screen"', page):
                meta['section'] = 'Screen'
            else:
                meta.pop('section', None)
            output = source_text(meta, article['body'])
            parse_markdown(output)
            destinations = exchange.sources(stage, slug) or [stage / 'content/drafts' / (slug + '.md')]
            for destination in destinations:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(output, encoding='utf-8')
        (stage / 'index.html').write_text(home, encoding='utf-8')
        namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
        ET.register_namespace('', namespace)
        sitemap = ET.parse(stage / 'sitemap.xml')
        for node in sitemap.getroot():
            url = node.findtext(f'{{{namespace}}}loc', '')
            if any(url.endswith('/stories/' + slug + '/') for slug in changes):
                modified = node.find(f'{{{namespace}}}lastmod')
                if modified is None:
                    modified = ET.SubElement(node, f'{{{namespace}}}lastmod')
                modified.text = date.today().isoformat()
        sitemap.write(stage / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
        build = subprocess.run([sys.executable, str(stage / 'scripts/build_content.py')], cwd=stage,
                               capture_output=True, text=True, encoding='utf-8',
                               env=dict(os.environ, PYTHONUTF8='1'))
        if build.returncode:
            raise ValueError('Site rebuild failed; no files changed:\n' + build.stdout + build.stderr)
        for slug in changes:
            validate_links(stage, slug, (stage / 'stories' / slug / 'index.html').read_text(encoding='utf-8'))
        writes = {}
        for candidate in stage.rglob('*'):
            if not candidate.is_file() or '__pycache__' in candidate.parts:
                continue
            relative = candidate.relative_to(stage)
            target = root / relative
            after = candidate.read_bytes()
            before = target.read_bytes() if target.exists() else None
            if before == after:
                continue
            # Ignore unrelated inter-tag whitespace normalisation from the builder.
            if before and relative.suffix == '.html' and relative.parts[:1] == ('stories',) and relative.parts[1] not in changes:
                normal = lambda b: re.sub(rb'>\s+<', b'><', b)
                if normal(before) == normal(after):
                    continue
            writes[target] = after
        # Refresh the bundle snapshot so a repeated import is a true no-op.
        writes[path] = exchange.bundle(stage).encode('utf-8')
        for slug, change in changes.items():
            print('Changed: ' + slug)
            if dry_run:
                before = json.dumps(change['live']['fields'], ensure_ascii=False, indent=2) + '\n\n' + change['live']['body'] + '\n'
                after = json.dumps(change['article']['fields'], ensure_ascii=False, indent=2) + '\n\n' + change['article']['body'] + '\n'
                print(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=slug+' (site)', tofile=slug+' (edited)')))
        print(f'{"Would update" if dry_run else "Updating"} {len(changes)} articles; {len(writes)} files including sources, metadata and editing bundle.')
        if dry_run:
            return list(changes)
        originals = {target: target.read_bytes() if target.exists() else None for target in writes}
        try:
            for target, data in writes.items():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        except OSError:
            for target, original in originals.items():
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    target.write_bytes(original)
            raise
    print('Updated the site and search. Review git diff, then commit and push when ready.')
    return list(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', nargs='?', type=Path, default=exchange.DEFAULT_OUTPUT)
    parser.add_argument('--dry-run', action='store_true', help='Validate and show edits without writing any files')
    args = parser.parse_args()
    path = args.markdown if args.markdown.is_absolute() else exchange.ROOT / args.markdown
    apply_bundle(exchange.ROOT, path, args.dry_run)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        sys.exit(f'import_articles: {exc}')
