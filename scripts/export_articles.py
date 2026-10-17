#!/usr/bin/env python3
"""Export current article copy to one editable Markdown bundle (Python stdlib only)."""
import argparse
from dataclasses import dataclass, field
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path('content/articles-edit.md')
BODY = re.compile(r'(<article class="article-body">)(.*?)(?=\s*<!-- topics:start -->)', re.S)
START = re.compile(r'^<!-- fourth-frame:article (\{.*\}) -->$', re.M)
END = '<!-- fourth-frame:end -->'
FIELDS = ('title', 'description', 'summary', 'deck')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def find(self, tag=None, cls=None):
        if (tag is None or self.tag == tag) and (cls is None or cls in self.attrs.get('class', '').split()):
            return self
        for child in self.children:
            if isinstance(child, Node):
                found = child.find(tag, cls)
                if found is not None:
                    return found
        return None


class Tree(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in {'img', 'hr', 'br', 'meta', 'link', 'input'}:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, text):
        self.stack[-1].children.append(text)


def plain(node):
    if node is None:
        return ''
    if isinstance(node, str):
        return node
    return ''.join(plain(c) for c in node.children)


def text(node):
    return ' '.join(plain(node).split())


def markdown_text(value):
    return re.sub(r'([\\`*\[\]])', r'\\\1', value.replace('\n', ' '))


def inline(node):
    if isinstance(node, str):
        return markdown_text(node)
    content = ''.join(inline(c) for c in node.children)
    if node.tag in {'em', 'i'}:
        return '*' + content + '*'
    if node.tag in {'strong', 'b'}:
        return '**' + content + '**'
    if node.tag == 'code':
        return '`' + plain(node) + '`'
    if node.tag == 'a':
        url = node.attrs['href'].replace('(', '%28').replace(')', '%29')
        return '[' + content + '](' + url + ')'
    if node.tag == 'sup' and 'source-ref' in node.attrs.get('class', '').split():
        return '[^' + text(node) + ']'
    if node.tag == 'span' and 'source-returns' in node.attrs.get('class', '').split():
        return ''
    if node.tag == 'br':
        return ' '
    raise ValueError(f'Unsupported inline <{node.tag}>; export stopped rather than dropping content')


def children_inline(node):
    return re.sub(r'\s+', ' ', ''.join(inline(c) for c in node.children)).strip()


def blocks(node):
    result = []
    for child in node.children:
        if isinstance(child, str):
            if child.strip():
                raise ValueError('Unexpected text outside an article block')
            continue
        tag, cls = child.tag, child.attrs.get('class', '')
        if tag == 'p':
            content = children_inline(child)
            if cls in {'spoiler-note', 'list-intro'}:
                content = f':::{cls}\n\n{content}\n\n:::end-note'
            elif cls:
                raise ValueError(f'Unsupported paragraph class {cls}')
            result.append(content)
        elif tag in {'h2', 'h3'}:
            result.append('#' * int(tag[1]) + ' ' + children_inline(child))
        elif tag in {'ul', 'ol'}:
            items = [c for c in child.children if isinstance(c, Node)]
            if any(c.tag != 'li' for c in items):
                raise ValueError('Unsupported list structure')
            result.append('\n'.join((f'{i}. ' if tag == 'ol' else '- ') + children_inline(c)
                                    for i, c in enumerate(items, 1)))
        elif tag == 'blockquote':
            result.append('> ' + children_inline(child.find('p') or child))
        elif tag == 'nav' and cls == 'article-contents':
            result.append('[TOC]')
        elif tag == 'section' and cls == 'article-footnotes':
            notes = child.find('ol')
            for note in notes.children:
                if isinstance(note, Node):
                    number = note.attrs['id'].removeprefix('source-note-')
                    result.append(f'[^{number}]: ' + children_inline(note.find('p')))
        elif tag == 'details' and cls == 'article-spoilers':
            result.append(':::spoilers ' + children_inline(child.find('summary')) + '\n\n' +
                          blocks(child.find('div', 'spoiler-body')) + '\n\n:::')
        elif tag == 'aside' and cls == 'related-stories' and child.attrs.get('aria-label') == 'Reporting sources':
            result.append(':::reporting-sources\n\n' + blocks(child) + '\n\n:::end-reporting-sources')
        elif tag == 'figure' and cls == 'article-figure':
            image, caption = child.find('img'), child.find('figcaption')
            if image is None or caption is None:
                raise ValueError('Incomplete figure')
            result.append(f'![{image.attrs["alt"]}]({image.attrs["src"]} "{text(caption)}")')
        elif tag == 'hr':
            result.append('---')
        else:
            raise ValueError(f'Unsupported article block <{tag} class="{cls}">')
    return '\n\n'.join(result)


def sources(root, slug):
    return [p for folder in ('drafts', 'journal')
            if (p := root / 'content' / folder / (slug + '.md')).exists()]


def inventory(root):
    entries = json.loads((root / 'content/articles.json').read_text(encoding='utf-8'))
    if len({e['slug'] for e in entries}) != len(entries):
        raise ValueError('Duplicate slugs in content/articles.json')
    return entries


def homepage_container(root, slug):
    tree = Tree((root / 'index.html').read_text(encoding='utf-8')).root
    target = f'stories/{slug}/'
    def walk(node, parents):
        if isinstance(node, str):
            return None
        if node.tag == 'a' and node.attrs.get('href') == target:
            for parent in reversed(parents):
                if any(c in parent.attrs.get('class', '').split()
                       for c in ('story', 'journal-entry', 'list-row', 'feature-copy')):
                    return parent
        for child in node.children:
            found = walk(child, parents + [node])
            if found is not None:
                return found
        return None
    return walk(tree, [])


def current(root, entry):
    slug = entry['slug']
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError(f'Invalid article slug: {slug}')
    page = (root / 'stories' / slug / 'index.html').read_text(encoding='utf-8')
    match = BODY.search(page)
    if match is None:
        raise ValueError(f'Missing article body in {slug}')
    tree = Tree(page).root
    header = tree.find('header', 'article-header')
    description = re.search(r'<meta name="description" content="([^"]*)"', page)
    if header is None or description is None:
        raise ValueError(f'Missing article header/description in {slug}')
    saved = {}
    from add_article import parse_markdown
    for path in sources(root, slug):
        saved, _ = parse_markdown(path.read_text(encoding='utf-8'))
        break
    card = homepage_container(root, slug)
    values = dict(title=text(header.find('h1')), description=unescape(description[1]),
                  summary=text(card.find('p')) if card is not None and card.find('p') else saved.get('summary', unescape(description[1])),
                  deck=text(header.find('p', 'article-deck')))
    body = blocks(Tree(match[2]).root).strip()
    fingerprint = digest(dict(fields=values, body=match[2], entry=entry,
                              sources={str(p.relative_to(root)):p.read_text(encoding='utf-8') for p in sources(root, slug)}))
    return dict(fields=values, body=body, fingerprint=fingerprint, page=page,
                body_html=match[2], source_meta=saved)


def edit_digest(fields, body):
    return digest(dict(fields=fields, body=body.strip()))


def bundle(root):
    entries = inventory(root)
    lines = ['# Fourth Frame: edit all articles', '',
             'Edit the quoted fields and Markdown below. Keep the fourth-frame comments intact.',
             'Refresh from the site (replaces this file): `python3 scripts/export_articles.py --overwrite`',
             'Preview: `python3 scripts/import_articles.py --dry-run`',
             'Apply: `python3 scripts/import_articles.py`', '',
             '<!-- fourth-frame:bundle ' + json.dumps(dict(version=1, slugs=[e['slug'] for e in entries])) + ' -->', '']
    for entry in entries:
        data = current(root, entry)
        marker = dict(slug=entry['slug'], sha256=data['fingerprint'],
                      edit_sha256=edit_digest(data['fields'], data['body']))
        lines.extend(['<!-- fourth-frame:article ' + json.dumps(marker) + ' -->', '---'])
        lines.extend(key + ': ' + json.dumps(data['fields'][key], ensure_ascii=False) for key in FIELDS)
        lines.extend(['---', '', data['body'], '', END, ''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--overwrite', action='store_true', help='Explicitly replace an existing editing bundle')
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists() and not args.overwrite:
        raise ValueError(f'{output} exists; use --overwrite only after importing or saving your edits')
    content = bundle(ROOT)  # Complete the export before opening the destination.
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding='utf-8')
    print(f'Exported {len(inventory(ROOT))} articles to {output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        sys.exit(f'export_articles: {exc}')
