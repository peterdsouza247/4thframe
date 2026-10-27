#!/usr/bin/env python3
"""Checks committed reviews are searchable and properly linked in the static site."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://peterdsouza247.github.io/4thframe/"
REVIEWS = [
    "dragon-age-veilguard-review",
    "jedi-survivor-review",
    "mass-effect-legendary-edition-review",
    "elden-ring-personal-review",
    "batman-arkham-asylum-review",
    "tomb-raider-2013-review",
    "halo-reach-review",
    "mortal-kombat-11-review",
    "god-of-war-2018-review",
]
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonicals = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href"))

def main():
    entries = json.loads((ROOT/"content/articles.json").read_text())
    search = json.loads((ROOT/"search-index.json").read_text())
    urls = {node.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            for node in ET.parse(ROOT/"sitemap.xml").getroot()}
    hub = (ROOT/"reviews/index.html").read_text()
    home = (ROOT/"index.html").read_text()
    assert "reviews/" in home
    assert BASE+"reviews/" in urls
    assert sum(1 for slug in REVIEWS if f"stories/{slug}/" in home) == len(REVIEWS)
    assert sum(1 for slug in REVIEWS if f"../stories/{slug}/" in hub) == len(REVIEWS)
    assert len({entry["slug"] for entry in entries}) == len(entries)
    assert len({entry["url"] for entry in search}) == len(search)
    for slug in REVIEWS:
        entry = next(e for e in entries if e["slug"] == slug)
        assert entry["type"] == "Long read" and "Reviews" in entry["tags"]
        page = ROOT/"stories"/slug/"index.html"
        assert page.exists()
        markup = page.read_text()
        parsed = Parser()
        parsed.feed(markup)
        assert BASE+"stories/"+slug+"/" in parsed.canonicals
        assert f"stories/{slug}/" in hub
        assert BASE+"stories/"+slug+"/" in urls
        article = next(item for item in search if item["url"] == f"stories/{slug}/")
        assert article["description"] and article["body"]
        assert ":::spoilers" not in article["body"]
        assert '<div class="article-end">' in markup and '<!-- topics:start -->' in markup
        for href in parsed.links:
            if href.startswith("../../stories/"):
                target = href.split("../../stories/",1)[1].strip("/")
                assert (ROOT/"stories"/target/"index.html").exists(), (slug, target)
    print(f"Verified {len(REVIEWS)} reviews, search, related links, canonicals and sitemap.")

if __name__ == "__main__":
    main()
