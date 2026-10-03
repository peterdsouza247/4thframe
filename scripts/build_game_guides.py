#!/usr/bin/env python3
"""Render editable game-guide data as static, progressively enhanced pages."""
from pathlib import Path
from html import escape as esc
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://peterdsouza247.github.io/4thframe/'


def render(g):
    events = {e['id']: e for e in g['events']}
    milestones = {m['value']: m for m in g['milestones']}
    assert len(events) == len(g['events']), 'Duplicate event ID'
    assert all(e['unlock'] in milestones for e in g['entries'])
    assert all(set(m['unlocks']) <= events.keys() for m in g['milestones'])
    assert all(set(c['route']) <= events.keys() for c in g['characters'])
    assert all(u['event'] in events for c in g['characters'] for u in c['updates'])
    mast = re.search(r'<header class="mast">.*?</header>', (ROOT/'guides/index.html').read_text(), re.S)[0]
    mast = mast.replace('href="../', 'href="../../').replace('href="./"', 'href="../"').replace(' aria-current="page"','')
    entries = ''
    for e in g['entries']:
        entries += f'''<article class="entry-card" id="start-{e['id']}"><p class="entry-audience">{esc(e['audience'])}</p><h3>{esc(e['title'])}</h3><p>{esc(e['why'])}</p><dl><dt>Know this much</dt><dd>{esc(e['need'])}</dd><dt>You can skip</dt><dd>{esc(e['skip'])}</dd><dt>The trade-off</dt><dd>{esc(e['tradeoff'])}</dd><dt>Go next</dt><dd>{esc(e['next'])}</dd></dl>'''
        if e['unlock'] != 'none':
            entries += f'''<button type="button" class="recap-button" data-entry="{e['id']}" hidden>Read earlier-story recap (spoilers)</button><noscript><p>For earlier-story outcomes, open the relevant timeline recaps below.</p></noscript>'''
        entries += '</article>'
    basics=''.join(f'<div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>' for title,text in g['basics'])
    options=''.join(f'<option value="{m["value"]}">{esc(m["label"])}</option>' for m in g['milestones'])
    chars=''.join(f'<option value="{c["id"]}">{esc(c["name"])}</option>' for c in g['characters'])
    timeline=''
    for i,e in enumerate(g['events']):
        year=str(e['year']) if e['year'] else 'TBA'
        timeline += f'''<article id="event-{e['id']}" class="timeline-event" data-event="{e['id']}" data-release="{i}" data-story="{e['chronology'] or i+1}" data-characters="{esc(' '.join(e['characters']))}" data-optional="{str(e['optional']).lower()}"><span class="timeline-year">{year}</span><div class="timeline-copy"><p class="event-era">{esc(e['era'])} · {esc(e['status'])}</p><h3>{esc(e['title'])}</h3><p>{esc(e['premise'])}</p><p class="event-why"><strong>Where it fits:</strong> {esc(e['why'])}</p>'''
        if e['recap']:
            timeline += f'''<details class="story-spoiler" data-spoiler="{e['id']}"><summary>Story outcomes: {esc(e['title'])} (spoilers)</summary><p>{esc(e['recap'])}</p></details><p class="locked-note" hidden>Story outcomes hidden. Choose a completed game above to unlock them.</p>'''
        timeline += '</div></article>'
    people=''
    for c in g['characters']:
        route=''.join(f'<li><a href="#event-{id}">{esc(events[id]["title"])}</a></li>' for id in c['route'])
        updates=''.join(f'<li data-spoiler="{u["event"]}"><strong>{esc(events[u["event"]]["title"])}:</strong> {esc(u["text"])}</li>' for u in c['updates'])
        people += f'''<article class="lore-character" id="character-{c['id']}"><p class="event-era">{esc(c['role'])}</p><h3>{esc(c['name'])}</h3><p>{esc(c['motivation'])}</p><p><strong>Connections:</strong> {esc(c['relationships'])}</p><details><summary>Follow this character</summary><ol>{route}</ol><button type="button" data-follow="{c['id']}" hidden>Show their timeline</button></details>'''
        if updates:
            people += f'<details class="character-outcomes"><summary>Story developments (spoilers)</summary><ul>{updates}</ul><p class="character-locked" hidden>Choose a completed game to see relevant developments.</p></details>'
        people+='</article>'
    factions=''.join(f'<div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>' for title,text in g['factions'])
    sources=''.join(f'<li><a href="{esc(url,quote=True)}">{esc(label)}</a></li>' for label,url in g['sources'])
    related=''.join(f'<li><a href="../../stories/{slug}/">{esc(title)}</a></li>' for title,slug in g['related'])
    payload = json.dumps(dict(entries=g['entries'], milestones=g['milestones']), ensure_ascii=False).replace('<','\\u003c')
    description=esc(g['description'],quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#171c28">
<title>{esc(g['name'])}: where to start, lore &amp; character guide | Fourth Frame</title><meta name="description" content="{description}"><link rel="canonical" href="{BASE}guides/{g['slug']}/"><meta property="og:type" content="article"><meta property="og:site_name" content="Fourth Frame"><meta property="og:title" content="{esc(g['name'])}: where to start"><meta property="og:description" content="{description}"><meta property="og:url" content="{BASE}guides/{g['slug']}/"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../../assets/style.css"><link rel="stylesheet" href="../../assets/game-guides.css"><script defer src="../../assets/game-guides.js"></script><script defer src="../../assets/analytics.js"></script></head>
<body><a class="skip" href="#main">Skip to content</a>{mast}
<main id="main" class="shell game-guide" data-series="{g['slug']}"><header class="lore-heading"><a class="guide-back" href="../">All guides</a><p class="eyebrow">Games / {esc(g['name'])}</p><h1>{esc(g['strap'])}</h1><p>{esc(g['intro'])}</p><p class="editor-pick"><strong>Our starting recommendation:</strong> {esc(g['recommendation'])}</p><nav class="lore-nav" aria-label="In this guide"><a href="#entry-points">Where to start</a><a href="#basics">Essential background</a><a href="#timeline">Timeline</a><a href="#characters">Characters</a><a href="#factions">World &amp; factions</a></nav></header>
<section id="entry-points" aria-labelledby="entry-title"><div class="section-head"><h2 id="entry-title">Choose your way in.</h2></div><div class="entry-grid">{entries}</div></section>
<section id="basics" aria-labelledby="basics-title"><div class="section-head"><h2 id="basics-title">Enough to begin.</h2></div><div class="basics-grid">{basics}</div></section>
<section id="timeline" aria-labelledby="timeline-title"><div class="section-head"><h2 id="timeline-title">The story, at your pace.</h2></div><p class="section-intro">Titles and starting premises are visible. Story outcomes stay hidden until you choose to reveal them. You can play a recommended route without completing this timeline.</p><noscript><p><strong>Spoiler note:</strong> controls require JavaScript. Every entry is readable below; open a “Story outcomes” or “Story developments” disclosure only if you accept its spoilers.</p></noscript>
<div class="timeline-controls" hidden><label>Spoilers allowed through<select id="spoiler-limit">{options}</select></label><label>Timeline order<select id="timeline-order"><option value="release">Release order</option><option value="story">Story order</option></select></label><label>Follow a character<select id="timeline-character"><option value="all">Everyone</option>{chars}</select></label><label class="timeline-toggle"><input type="checkbox" id="recommended-only"> Main story route only</label></div>
<p class="timeline-help">{'Warcraft’s release and journey order broadly align. Warlords of Draenor is an alternate-history detour after Pandaria, not the original past. “Main story route” highlights Warcraft III and the Worldsoul Saga; older expansions remain optional context.' if g['slug']=='warcraft' else 'Story order places DLC within its campaign, before the final resolution. Andromeda’s expedition leaves during the trilogy era but its playable story occurs much later. “Main story route” shows the three Shepard games; Andromeda remains a separate entry point.'}</p><p id="timeline-status" role="status" aria-live="polite"></p><div id="story-timeline">{timeline}</div><p id="timeline-empty" hidden>No entries match both choices. Show everyone or turn off the main-story filter.</p></section>
<section id="characters" aria-labelledby="characters-title"><div class="section-head"><h2 id="characters-title">People worth knowing.</h2></div><p class="section-intro">Start with who they are and what drives them. Their routes show relevant appearances, not a list of games you must finish. Development notes follow your spoiler setting.</p><div class="character-grid">{people}</div></section>
<section id="factions" aria-labelledby="factions-title"><div class="section-head"><h2 id="factions-title">The bigger picture.</h2></div><div class="faction-grid">{factions}</div></section>
<section class="lore-scope" aria-labelledby="scope-title"><h2 id="scope-title">Sources and scope</h2><p>Reviewed 3 October 2026. Entry points, optional routes, and play order are Fourth Frame’s editorial recommendations.</p><p>{esc(g['scope'])}</p><details><summary>Reference material (may contain spoilers)</summary><ul>{sources}</ul></details><p>Editable guide data: <a href="../../content/guides/{g['slug']}.json">{esc(g['name'])} source</a>.</p><h3>Keep reading</h3><ul>{related}</ul></section>
<dialog id="recap-dialog" aria-labelledby="recap-title"><button id="recap-close" type="button" autofocus>Close recap</button><h2 id="recap-title">Before you begin</h2><p id="recap-intro"></p><div id="recap-body"></div><p>You have enough context to begin. Return to the deeper guide whenever a name or event becomes relevant.</p></dialog>
<script type="application/json" id="game-guide-data">{payload}</script></main><footer class="footer shell"><span>Fourth Frame · Writing by Peter D’Souza</span><a href="#main">Back to top ↑</a></footer></body></html>'''


def main():
    guides=[json.loads((ROOT/'content/guides'/f'{slug}.json').read_text()) for slug in ('warcraft','mass-effect')]
    for g in guides:
        out=ROOT/'guides'/g['slug']/'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(render(g))
    # The guide catalogue shares the existing search/filter controls.
    cards=''
    for i,g in enumerate(guides,108):
        search=' '.join([g['name'],g['description']]+[e['title'] for e in g['events']]+[c['name'] for c in g['characters']]).lower()
        cards+=f'''<article class="guide-card game-route" data-universe="{esc(g['name'])}" data-medium="games" data-name="{g['name'].lower()}" data-core-count="{len(g['entries'])}" data-search="{esc(search,quote=True)}"><div class="guide-card-top"><span class="guide-index">{i}</span><span class="guide-universe">{esc(g['name'])} / Play</span></div><h3><a href="{g['slug']}/">{esc(g['name'])}: where to start</a></h3><p>{esc(g['description'])}</p><p class="guide-card-summary">{len(g['entries'])} entry points · {len(g['characters'])} character guides</p><a class="game-guide-link" href="{g['slug']}/">Explore the guide</a></article>'''
    path=ROOT/'guides/index.html'
    page=path.read_text()
    page=re.sub(r'<!-- game-guides:start -->.*?<!-- game-guides:end -->','',page,flags=re.S)
    marker='<section class="guide-grid" id="guide-grid" aria-label="Character routes">'
    assert marker in page
    page=page.replace(marker,marker+'<!-- game-guides:start -->'+cards+'<!-- game-guides:end -->')
    page=page.replace('Character watch and reading guides | Fourth Frame','World, character and playing guides | Fourth Frame')
    page=page.replace('Follow the character.','Find your way into a world.')
    page=page.replace('Choose whose story you want to follow. Core steps carry the major turns; optional entries add context, alternate takes or a worthwhile detour. Read each route from top to bottom.','Choose a game series or a character. Find a welcoming starting point, follow the essential story, and take the optional detours that interest you.')
    page=page.replace('Follow Marvel, Star Wars, X-Men, Justice League and Avengers characters through curated core and optional screen and comics routes.','Find where to start Warcraft and Mass Effect, or follow Marvel, Star Wars and DC characters through watch and reading routes.')
    page=page.replace('Pick a character. See the core story and the optional detours worth taking.','Find a welcoming starting point, the essential story, and optional detours worth taking.')
    if 'data-medium="games" aria-pressed' not in page:
        page=page.replace('<button type="button" class="kind-button" data-medium="comics"','<button type="button" class="kind-button" data-medium="games" aria-pressed="false">Play</button><button type="button" class="kind-button" data-medium="comics"',1)
    if 'data-universe="Warcraft" aria-pressed' not in page:
        page=page.replace('<button type="button" data-universe="MCU"','<button type="button" data-universe="Warcraft" aria-pressed="false">Warcraft</button><button type="button" data-universe="Mass Effect" aria-pressed="false">Mass Effect</button><button type="button" data-universe="MCU"',1)
    page=page.replace('<link rel="stylesheet" href="../assets/style.css">','<link rel="stylesheet" href="../assets/style.css"><link rel="stylesheet" href="../assets/game-guides.css">') if 'href="../assets/game-guides.css"' not in page else page
    page=page.replace('107 routes. Select a card to read its path.','109 guides. Choose a series or character to begin.')
    page=page.replace('Character or title</label>','Series, character or title</label>').replace('Character A–Z','Name A–Z')
    roadmap=json.loads((ROOT/'content/guides/game-roadmap.json').read_text())
    future='<section class="game-roadmap"><h2>Next worlds to explore</h2><p>Planned guides: '+esc(', '.join(roadmap))+'.</p></section>'
    page=re.sub(r'<!-- game-roadmap:start -->.*?<!-- game-roadmap:end -->','',page,flags=re.S)
    page=page.replace('</main>','<!-- game-roadmap:start -->'+future+'<!-- game-roadmap:end --></main>')
    path.write_text(page)
    # Site search deliberately indexes entry-point copy only, never plot outcomes.
    index_path=ROOT/'search-index.json'
    rows=json.loads(index_path.read_text())
    rows=[r for r in rows if r['url'] not in [f'guides/{g["slug"]}/' for g in guides]]
    for g in guides:
        rows.append(dict(title=f'{g["name"]}: where to start',url=f'guides/{g["slug"]}/',type='Guide',description=g['description'],tags=[g['name'],'Guides','Lore'],body=' '.join([g['intro'],g['recommendation']]+[' '.join(str(e[k]) for k in ('title','audience','why','need','skip','tradeoff','next')) for e in g['entries']]+[c['name'] for c in g['characters']])))
    index_path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    namespace='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',namespace)
    sitemap=ET.parse(ROOT/'sitemap.xml')
    urls={el.text for el in sitemap.findall(f'.//{{{namespace}}}loc')}
    for g in guides:
        url=BASE+'guides/'+g['slug']+'/'
        if url not in urls:
            ET.SubElement(ET.SubElement(sitemap.getroot(),f'{{{namespace}}}url'),f'{{{namespace}}}loc').text=url
    sitemap.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    print('Built Warcraft and Mass Effect guides; updated catalogue, safe search entries, and sitemap.')


if __name__=='__main__':
    main()
