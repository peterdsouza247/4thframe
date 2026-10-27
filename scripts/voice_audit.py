#!/usr/bin/env python3
"""Non-destructive Fourth Frame prose scan. Editorial prompts, not automatic rewrites."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "generic superlative": r"\b(?:a masterclass in|a breathtaking journey|an unparalleled experience)\b",
    "stock opener": r"\b(?:in the ever-evolving landscape|in today's fast-paced world|delve into)\b",
    "empty proclamation": r"\b(?:stands as a testament to|one thing is clear|it's safe to say)\b",
    "formulaic contrast": r"\bnot (?:just|merely)\b.{0,85}\bbut\b",
    "filler transition": r"\b(?:in conclusion|at its core|needless to say)\b",
}
def main():
    paths = [ROOT / p for p in sys.argv[1:]] if len(sys.argv) > 1 else sorted((ROOT / "content/drafts").glob("*.md"))
    hits = 0
    for path in paths:
        for num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith(("title:", "description:", "summary:", "tags:", "related:")):
                continue
            for label, pattern in PATTERNS.items():
                if re.search(pattern, line, re.I):
                    print(f"{path.relative_to(ROOT)}:{num}: {label}: {line.strip()[:125]}")
                    hits += 1
    print(f"{hits} editorial flag(s); review context manually before making changes.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
