#!/usr/bin/env python3
"""Keep the static Reviews archive aligned with homepage review cards."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
ARCHIVE = ROOT / "reviews/index.html"


def sync_reviews():
    home = HOME.read_text()
    page = ARCHIVE.read_text()
    section = re.search(r'<section class="shell" id="reviews".*?</section>', home, re.S)
    if not section:
        raise ValueError("Reviews homepage section is missing")
    cards = re.findall(r'<article class="story">.*?</article>', section.group(), re.S)
    if not cards:
        raise ValueError("Reviews homepage section contains no cards")
    cards = [card.replace('href="stories/', 'href="../stories/') for card in cards]
    pattern = r'(<section class="shell" aria-label="Personal game reviews"><div class="stories">\s*).*?(</div><p>Older reviews)'
    updated, count = re.subn(pattern,
        lambda m: m.group(1) + "\n".join(cards) + "\n" + m.group(2),
        page, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Reviews archive card container is missing")
    if updated != page:
        ARCHIVE.write_text(updated)
    print(f"Synced {len(cards)} review cards to reviews/index.html")


if __name__ == "__main__":
    sync_reviews()
