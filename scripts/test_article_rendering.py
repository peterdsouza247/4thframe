#!/usr/bin/env python3
"""Regression checks for long-read navigation, source notes and safe Markdown."""
import unittest
from add_article import render_body


class LongReadRendering(unittest.TestCase):
    def test_notes_link_back_to_every_reference(self):
        html = render_body('First.[^2] Again.[^2]\n\n[^2]: A [source](https://example.com) & context.')
        for number in (1, 2):
            self.assertIn(f'id="source-ref-2-{number}"', html)
            self.assertIn(f'href="#source-ref-2-{number}" role="doc-backlink"', html)
        self.assertIn('id="source-note-2" value="2"', html)
        self.assertIn('href="https://example.com"', html)
        self.assertIn('&amp; context', html)
        self.assertNotIn('[^2]', html)

    def test_invalid_notes_fail_before_publishing(self):
        for body in ('Missing.[^1]', 'Text.\n\n[^1]: Unused.',
                     'Text.[^1]\n\n[^1]: First.\n[^1]: Duplicate.'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                render_body(body)

    def test_contents_handles_duplicate_headings_and_escaping(self):
        html = render_body('[TOC]\n\n## City & *crime*\n\n### A detour\n\n## City & *crime*')
        self.assertIn('id="city-crime"', html)
        self.assertIn('id="city-crime-2"', html)
        self.assertIn('id="a-detour"', html)
        self.assertIn('href="#city-crime-2">City &amp; crime</a>', html)
        self.assertNotIn('href="#a-detour"', html)  # Contents lists chapters, not subheads.
        self.assertNotIn('[TOC]', html)

    def test_code_and_html_remain_safe(self):
        html = render_body('`[^1]` <script>alert(1)</script> [bad](https://example.com)')
        self.assertIn('<code>[^1]</code>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        with self.assertRaises(ValueError):
            render_body('[bad](javascript:alert)')

    def test_existing_plain_markdown_is_unchanged(self):
        self.assertEqual(render_body('## Heading\n\nA **bold** word.\n\n- One\n- Two'),
                         '<h2>Heading</h2>\n<p>A <strong>bold</strong> word.</p>\n<ul><li>One</li><li>Two</li></ul>')

    def test_spoilers_are_collapsed_and_absent_from_contents(self):
        html = render_body('[TOC]\n\n## Verdict\n\n:::spoilers Read the spoilers\n\n## Secret identity\n\n<script>twist</script>\n\n:::')
        self.assertIn('<details class="article-spoilers"><summary>Read the spoilers</summary>', html)
        self.assertNotIn('<details class="article-spoilers" open', html)
        self.assertIn('&lt;script&gt;twist&lt;/script&gt;', html)
        self.assertNotIn('href="#secret-identity"', html)

    def test_spoiler_markers_must_balance(self):
        for body in (':::spoilers Warning\n\nSecret', ':::',
                     ':::spoilers First\n\n:::spoilers Second\n\n:::'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                render_body(body)


if __name__ == '__main__':
    unittest.main()
