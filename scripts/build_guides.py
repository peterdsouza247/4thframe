#!/usr/bin/env python3
"""Build the static character-guide page from the editable Markdown guides."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / 'content/guides/screen.md'
COMICS = ROOT / 'content/guides/comics.md'
OUT = ROOT / 'guides/index.html'
DATA = ROOT / 'content/guides.json'


def plain(value):
    value = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', value)
    return value.replace('**', '').replace('*', '').replace('`', '').strip()


def parse(path, medium):
    universe = None
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if medium == 'screen' and line.startswith('## '):
            universe = {'Marvel Cinematic Universe': 'MCU', 'Star Wars': 'Star Wars'}.get(line[3:].strip(), universe)
        elif medium == 'comics' and line.startswith('## '):
            universe = {'1. Original X-Men': 'X-Men', '2. Original Justice League of America': 'Justice League', '3. Original Avengers': 'Avengers'}.get(line[3:].strip(), universe)
        if not line.startswith('|') or line.startswith('|---') or line.startswith('| Character') or line.startswith('| Member') or line.startswith('| Founding member') or line.startswith('| Team'):
            continue
        fields = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(fields) != 3 or not universe or fields[0] in ('Character', 'Member', 'Founding member'):
            continue
        # The first comics table is roster comparison, not a character route.
        if medium == 'comics' and not any(mark in fields[1] for mark in ('*', '→')):
            continue
        name = plain(fields[0])
        if medium == 'comics' and name.startswith(('X-Men,', 'Justice League of America,', 'Avengers,')):
            continue
        core = [plain(item) for item in fields[1].split('→')]
        extras = [plain(item) for item in fields[2].split('; ')]
        rows.append(dict(name=name, universe=universe, medium=medium, core=core, extras=extras,
                         core_text=plain(fields[1]), extras_text=plain(fields[2])))
    return rows


routes = parse(SCREEN, 'screen') + parse(COMICS, 'comics')
assert len(routes) >= 95, f'Guide parsing lost entries: {len(routes)}'
DATA.write_text(json.dumps(routes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def esc(value): return html.escape(value, quote=True)


def card(route, idx):
    core = ''.join(f'<li>{esc(item)}</li>' for item in route['core'])
    extras = ''.join(f'<li>{esc(item)}</li>' for item in route['extras'])
    search = ' '.join((route['name'], route['universe'], route['core_text'], route['extras_text'])).casefold()
    return f'''<article class="guide-card" data-universe="{esc(route['universe'])}" data-medium="{route['medium']}" data-name="{esc(route['name'].casefold())}" data-core-count="{len(route['core'])}" data-search="{esc(search)}">
      <div class="guide-card-top"><span class="guide-index">{idx:03d}</span><span class="guide-universe">{esc(route['universe'])} / {'Watch' if route['medium']=='screen' else 'Read'}</span></div>
      <h3>{esc(route['name'])}</h3><p class="guide-card-summary">{len(route['core'])} core steps · {len(route['extras'])} optional notes</p>
      <details><summary>Open the route <span aria-hidden="true">↗</span></summary>
        <div class="guide-card-body"><h4>Core route <span>in order</span></h4><ol>{core}</ol>
        <div class="optional-route"><h4>Optional <span>and why</span></h4><ul>{extras}</ul></div></div>
      </details>
    </article>'''

cards = '\n'.join(card(route, i) for i, route in enumerate(routes, 1))
page = '''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#171c28">
<title>Character watch and reading guides | Fourth Frame</title>
<meta name="description" content="Follow Marvel, Star Wars, X-Men, Justice League and Avengers characters through curated core and optional screen and comics routes.">
<link rel="canonical" href="https://peterdsouza247.github.io/4thframe/guides/">
<meta property="og:type" content="website"><meta property="og:site_name" content="Fourth Frame"><meta property="og:title" content="Character watch and reading guides | Fourth Frame"><meta property="og:description" content="Pick a character. See the core story and the optional detours worth taking."><meta property="og:url" content="https://peterdsouza247.github.io/4thframe/guides/">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../assets/style.css">
<script defer src="../assets/guides.js"></script><script defer src="../assets/analytics.js"></script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="shell"><div class="mast-top"><span>Independent games &amp; culture writing</span><span>Vol. 01 / A different angle on familiar worlds</span></div><div class="mast-row"><a class="wordmark" href="../" aria-label="Fourth Frame home">Fourth<i>.</i>Frame</a><p class="mast-right">Stories worth revisiting.<br>By Peter D’Souza.</p></div><nav class="nav" aria-label="Sections"><a href="../#long-reads">Long reads</a><a href="../#lists">Lists</a><a href="./" aria-current="page">Guides</a><a href="../search/">Search</a><a href="../#about">About</a><span>Go deeper ↗</span></nav></div></header>
<main id="main" class="shell guides-page">
  <header class="guides-heading"><span class="eyebrow">III / The routes</span><h1>Follow the character.</h1><p>Choose whose story you want to follow. Core steps carry the major turns; optional entries add context, alternate takes or a worthwhile detour. Read each route from top to bottom.</p><div class="guide-line" aria-hidden="true"><span></span><span></span><span></span><span></span></div></header>
  <section class="guide-controls" aria-label="Find a route">
    <div class="guide-kind" role="group" aria-label="Medium"><button type="button" class="kind-button" data-medium="all" aria-pressed="true">All</button><button type="button" class="kind-button" data-medium="screen" aria-pressed="false">Watch</button><button type="button" class="kind-button" data-medium="comics" aria-pressed="false">Read</button></div>
    <div class="guide-filters" role="group" aria-label="Universe"><button type="button" data-universe="all" aria-pressed="true">All worlds</button><button type="button" data-universe="MCU" aria-pressed="false">MCU</button><button type="button" data-universe="Star Wars" aria-pressed="false">Star Wars</button><button type="button" data-universe="X-Men" aria-pressed="false">X-Men</button><button type="button" data-universe="Justice League" aria-pressed="false">Justice League</button><button type="button" data-universe="Avengers" aria-pressed="false">Avengers</button></div>
    <div class="guide-tools"><label class="guide-search">Character or title<input id="guide-search" type="search" placeholder="Try Ahsoka, Jean Grey, Thor…" autocomplete="off"></label><label class="guide-sort">Sort by<select id="guide-sort"><option value="editorial">Guide order</option><option value="name">Character A–Z</option><option value="shortest">Shortest core first</option><option value="longest">Longest core first</option></select></label><label class="guide-toggle"><input id="core-only" type="checkbox"><span>Core steps only</span></label></div>
  </section>
  <p class="guide-status" id="guide-status" role="status" aria-live="polite">__COUNT__ routes. Select a card to read its path.</p>
  <section class="guide-grid" id="guide-grid" aria-label="Character routes">__CARDS__</section>
  <p class="guide-empty" id="guide-empty" hidden>No routes match those choices. Try another character or clear a filter.</p>
  <section class="guide-notes" aria-labelledby="guide-notes-title"><div class="section-head"><span class="section-id">The context</span><h2 id="guide-notes-title">Before you begin</h2></div>
    <div class="guide-note-grid"><div><h3>Screen continuity</h3><p>MCU paths follow the shared live-action films and shows, with separate-universe appearances labelled as optional. Star Wars paths use the main screen canon, including animation when it carries the story. “Core” is an editorial choice for that character, not a franchise-wide rule.</p></div><div><h3>Comics continuity</h3><p>The X-Men path starts with Cyclops, Jean, Beast, Angel and Iceman. The original Justice League has seven founders; the New 52 origin swaps Martian Manhunter for Cyborg. The Avengers begin with Iron Man, Thor, Hulk, Hank Pym and Janet van Dyne; Captain America joins in issue #4.</p></div><div><h3>Team entry points</h3><p><strong>X-Men:</strong> <em>X-Men</em> (1963) #1, #12–16 → <em>Giant-Size X-Men</em> #1 → <em>Uncanny X-Men</em> #129–137 → <em>X-Factor</em> #1–6, #18–26, #65–68.</p><p><strong>Justice League:</strong> <em>Brave and the Bold</em> #28 → <em>JLA</em> #9 → <em>DC: The New Frontier</em> #1–6 (separate retelling) → <em>JLA</em> (1997) #1–9, #43–46.</p><p><strong>Avengers:</strong> <em>Avengers</em> (1963) #1–4, #16, #54–58, #227–230, #273–277 → <em>Avengers</em> (1998) #1–4, #500–503 and <em>Avengers Finale</em> #1.</p></div></div>
    <details class="guide-sources"><summary>Sources and scope</summary><p>Updated 28 September 2026. These routes cover released screen stories and selected comics through that date. A character's available story may remain unfinished. Issue numbers matter more than collection names, which vary by edition.</p><p>Official references: <a href="https://www.marvel.com/movies">Marvel films</a>, <a href="https://www.marvel.com/tv-shows">Marvel series</a>, <a href="https://www.starwars.com/news/star-wars-movies-and-series-guide">Star Wars screen guide</a>, <a href="https://www.marvel.com/comics/guides/1726/avengers-origin">Avengers origin</a>, <a href="https://www.dc.com/blog/2021/03/17/us-united-how-almost-every-justice-league-was-formed">Justice League formations</a>. The complete, editable source guides are <a href="../content/guides/screen.md">screen</a> and <a href="../content/guides/comics.md">comics</a>.</p></details>
  </section>
</main><footer class="footer shell"><span>Fourth Frame · Writing by Peter D’Souza</span><a href="#main">Back to top ↑</a></footer>
</body></html>'''
OUT.write_text(page.replace('__COUNT__', str(len(routes))).replace('__CARDS__', cards), encoding='utf-8')
print(f'Built {len(routes)} character routes ({sum(r["medium"]=="screen" for r in routes)} screen, {sum(r["medium"]=="comics" for r in routes)} comics)')
