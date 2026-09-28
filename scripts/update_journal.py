#!/usr/bin/env python3
"""Rebuild an existing Development Journal page from its editable Markdown."""

from pathlib import Path
import json
import re
import subprocess
import sys

import add_article as publisher


def main(source: Path) -> None:
    meta, body = publisher.parse_markdown(source.read_text(encoding="utf-8-sig"))
    if meta["type"] != "Journal":
        raise ValueError('Journal updates require type: "Journal"')
    slug = meta["slug"]
    target = publisher.STORIES / slug / "index.html"
    if not target.exists():
        raise ValueError(f"Unknown journal slug {slug}; use add_article.py first")
    entries = json.loads(publisher.ARTS.read_text())
    entry = next((item for item in entries if item["slug"] == slug and item["type"] == "Journal"), None)
    if entry is None:
        raise ValueError(f"{slug} is not a journal entry")
    related = meta.get("related", [])
    known = {item["slug"] for item in entries} - {slug}
    if len(related) != len(set(related)) or not set(related) <= known:
        raise ValueError("related must contain unique existing articles other than this entry")
    minutes = max(1, round(len(re.findall(r"\b[\w’'-]+\b", body)) / 220))
    page = publisher.article_html(meta, publisher.render_body(body), minutes)
    home = publisher.HOME.read_text()
    pattern = rf'<article class="journal-entry">(?:(?!</article>).)*?href="stories/{re.escape(slug)}/"(?:(?!</article>).)*?</article>'
    home, count = re.subn(pattern, lambda _: publisher.homepage_card(meta, minutes).strip(), home, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"Could not find the {slug} homepage card")
    entry.update(tags=meta["tags"], related=related)
    if meta.get("published"):
        entry["published"] = meta["published"]
    else:
        entry.pop("published", None)
    target.write_text(page)
    publisher.HOME.write_text(home)
    publisher.ARTS.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    subprocess.run([sys.executable, str(publisher.ROOT / "scripts/build_content.py")], check=True)
    print(f"Updated {slug} and refreshed search metadata")


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except (IndexError, ValueError, OSError) as exc:
        sys.exit(f"update_journal: {exc}")
