#!/usr/bin/env python3
"""Integration checks for bulk editing against the real site's full article inventory."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

import export_articles as exchange
import import_articles as importer
from add_article import parse_markdown, render_body


def file_hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def article_text(markup):
    tree = exchange.Tree(markup).root
    def walk(node):
        if isinstance(node, str):
            return node
        if node.tag == 'nav' or 'source-returns' in node.attrs.get('class', '').split():
            return ''
        return ' '.join(walk(child) for child in node.children)
    return ' '.join(walk(tree).split())


class ArticleExchange(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'site'
        shutil.copytree(exchange.ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.path = self.root / 'content/articles-edit.md'
        self.path.write_text(exchange.bundle(self.root))

    def apply(self, dry_run=False):
        with redirect_stdout(io.StringIO()):
            return importer.apply_bundle(self.root, self.path, dry_run)

    def edit(self, slug, change_body=None, **fields):
        content = self.path.read_text()
        match = next(m for m in exchange.START.finditer(content) if json.loads(m[1])['slug'] == slug)
        end = content.index(exchange.END, match.end())
        section = content[match.end():end]
        for key, value in fields.items():
            section = re.sub(r'^' + key + r': .*$', lambda _:key + ': ' + json.dumps(value, ensure_ascii=False), section, flags=re.M)
        if change_body:
            section = section.rstrip() + '\n\n' + change_body + '\n\n'
        self.path.write_text(content[:match.end()] + section + content[end:])

    def test_unedited_export_is_byte_identical(self):
        before = file_hashes(self.root)
        self.assertEqual(self.apply(), [])
        self.assertEqual(file_hashes(self.root), before)

    def test_every_article_can_be_edited_without_losing_existing_text(self):
        originals = {}
        for entry in exchange.inventory(self.root):
            slug = entry['slug']
            originals[slug] = article_text(exchange.current(self.root, entry)['body_html'])
            self.edit(slug, 'Bulk editing check: preserve every earlier paragraph.')
        changed = self.apply()
        self.assertEqual(set(changed), set(originals))
        for entry in exchange.inventory(self.root):
            slug = entry['slug']
            live = exchange.current(self.root, entry)
            actual = article_text(live['body_html'])
            # Endnotes remain at the end, so the inserted prose can precede them.
            self.assertEqual(actual.replace('Bulk editing check: preserve every earlier paragraph.', '').split(), originals[slug].split(), slug)
            paths = exchange.sources(self.root, slug)
            self.assertTrue(paths, slug)
            for source in paths:
                meta, body = parse_markdown(source.read_text())
                self.assertEqual(render_body(body).strip(), live['body_html'].strip(), slug)
                if slug == 'best-jonathan-hickman-comics':
                    self.assertNotIn('section', meta)
                if slug == 'why-heroes-is-still-worth-watching':
                    self.assertEqual(meta['section'], 'Screen')
        before = file_hashes(self.root)
        self.assertEqual(self.apply(), [])
        self.assertEqual(before, file_hashes(self.root))
        search = json.loads((self.root / 'search-index.json').read_text())
        self.assertTrue(any(row['url'] == 'guides/jonathan-hickman/' for row in search))

    def test_titles_summaries_decks_and_search_stay_in_sync(self):
        slug = 'best-jonathan-hickman-comics'
        self.edit(slug, 'A new **paragraph** with *emphasis* and a [guide](../../guides/jonathan-hickman/).',
                  title='Hickman & the future', summary='A revised homepage summary.',
                  description='A revised search description.', deck='A new introduction beneath the title.')
        self.assertEqual(self.apply(), [slug])
        page = (self.root / 'stories' / slug / 'index.html').read_text()
        home = (self.root / 'index.html').read_text()
        self.assertIn('<h1>Hickman &amp; the future</h1>', page)
        self.assertIn('<title>Hickman &amp; the future | Fourth Frame</title>', page)
        self.assertIn('property="og:title" content="Hickman &amp; the future"', page)
        self.assertIn('class="article-deck">A new introduction beneath the title.', page)
        self.assertIn('>Hickman &amp; the future</a>', home)
        self.assertIn('<p>A revised homepage summary.</p>', home)
        search = json.loads((self.root / 'search-index.json').read_text())
        row = next(r for r in search if r['url'] == f'stories/{slug}/')
        self.assertEqual(row['title'], 'Hickman & the future')
        self.assertEqual(row['description'], 'A revised search description.')
        self.assertIn('A new paragraph', row['body'])
        self.assertIn('Hickman &amp; the future', (self.root / 'stories/comic-book-writers-worth-following/index.html').read_text())

    def test_featured_article_and_styled_paragraphs_survive(self):
        slug = 'telltales-batman-reinvention'
        self.edit(slug, 'An additional observation.', title='A revised Batman title', summary='A revised featured summary.')
        self.apply()
        page = (self.root / 'stories' / slug / 'index.html').read_text()
        self.assertIn('<p class="spoiler-note">', page)
        self.assertIn('<h2 id="hero-title">A revised Batman title</h2>', (self.root / 'index.html').read_text())

    def test_dry_run_has_no_side_effects(self):
        self.edit('best-ed-brubaker-comics', 'Preview only.')
        before = file_hashes(self.root)
        self.assertEqual(self.apply(True), ['best-ed-brubaker-comics'])
        self.assertEqual(before, file_hashes(self.root))

    def test_stale_edited_article_cannot_overwrite_a_newer_site(self):
        slug = 'best-grant-morrison-comics'
        self.edit(slug, 'My offline edit.')
        page = self.root / 'stories' / slug / 'index.html'
        page.write_text(page.read_text().replace('A living street.', 'A newly revised living street.', 1))
        before = file_hashes(self.root)
        with self.assertRaisesRegex(ValueError, 'changed since export'):
            self.apply()
        self.assertEqual(before, file_hashes(self.root))

    def test_invalid_second_article_does_not_apply_the_first(self):
        self.edit('best-jonathan-hickman-comics', 'A valid edit.')
        self.edit('best-alan-moore-comics', 'An undefined reference.[^999]')
        before = file_hashes(self.root)
        with self.assertRaisesRegex(ValueError, 'Missing source note'):
            self.apply()
        self.assertEqual(before, file_hashes(self.root))

    def test_missing_duplicate_and_unknown_sections_are_rejected(self):
        source = self.path.read_text()
        first = exchange.START.search(source)
        end = source.index(exchange.END, first.end()) + len(exchange.END)
        for content in [source[:first.start()] + source[end:], source + '\n' + source[first.start():end],
                        source.replace('"slug": "telltales-batman-reinvention"', '"slug": "../outside"', 1)]:
            with self.subTest(content=content[-50:]), self.assertRaises(ValueError):
                importer.read_bundle(content)

    def test_broken_local_link_is_caught_before_writing(self):
        self.edit('best-alan-moore-comics', '[A missing page](../../stories/does-not-exist/)')
        before = file_hashes(self.root)
        with self.assertRaisesRegex(ValueError, 'missing local link'):
            self.apply()
        self.assertEqual(before, file_hashes(self.root))

    def test_literal_markdown_characters_are_preserved(self):
        html = '<p>Use * literally, [brackets], and a backslash \\ here.</p>'
        md = exchange.blocks(exchange.Tree(html).root)
        self.assertEqual(article_text(render_body(md)), article_text(html))

    def test_export_uses_site_body_when_a_saved_draft_is_stale(self):
        slug = 'best-ed-brubaker-comics'
        source = self.root / 'content/drafts' / (slug + '.md')
        source.write_text(source.read_text().replace('Someone in an Ed Brubaker comic', 'STALE DRAFT BODY', 1))
        data = exchange.current(self.root, next(e for e in exchange.inventory(self.root) if e['slug'] == slug))
        self.assertNotIn('STALE DRAFT BODY', data['body'])
        self.assertIn('Someone in an Ed Brubaker comic', data['body'])

    def test_link_label_formatting_and_code_remain_safe(self):
        self.assertEqual(render_body(r'[A *word* and \[literal\]](https://example.com)'),
                         '<p><a href="https://example.com">A <em>word</em> and [literal]</a></p>')
        self.assertEqual(render_body('`[code](https://example.com)`'),
                         '<p><code>[code](https://example.com)</code></p>')
        with self.assertRaises(ValueError):
            render_body('[bad](javascript:alert)')

    def test_local_images_keep_their_alt_text_and_credit(self):
        image = self.root / 'assets/images/editor-check.svg'
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
        slug = 'best-alan-moore-comics'
        self.edit(slug, '![An editorial image](../../assets/images/editor-check.svg "Original artwork credit")')
        self.apply()
        page = (self.root / 'stories' / slug / 'index.html').read_text()
        self.assertIn('src="../../assets/images/editor-check.svg" alt="An editorial image"', page)
        self.assertIn('<figcaption>Original artwork credit</figcaption>', page)
        self.assertIn('![An editorial image]', self.path.read_text())
        with self.assertRaises(ValueError):
            render_body('![Bad](../../assets/images/../../README.md "Bad traversal")')


if __name__ == '__main__':
    unittest.main()
