#!/usr/bin/env python3
"""Progressively enhanced timelines for the existing editorial screen routes."""
from pathlib import Path
from html import escape as esc
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://peterdsouza247.github.io/4thframe/'


def route_id(route):
    return re.sub(r'[^a-z0-9]+', '-', (route['universe']+'-'+route['name']).lower()).strip('-')


def steps(route, titles):
    result=[]
    previous=None
    for index, raw in enumerate(route['core']):
        if raw.startswith('No film/series path:'):
            return []
        label=(previous+' '+raw) if re.match(r'^S\d',raw) and previous else raw
        matches=[m for m in titles if label.startswith(m['title'])]
        assert matches, f'Unmapped screen step: {route["name"]}: {label}'
        meta=max(matches,key=lambda m:len(m['title']))
        previous=meta['title']
        years=[]
        for first,last in re.findall(r'S(\d+)(?:[–-](\d+))?',label):
            for season in range(int(first),int(last or first)+1):
                assert str(season) in meta.get('seasons',{str(season):meta['year']}), f'Unknown season: {label}'
                years.append(meta.get('seasons',{}).get(str(season),meta['year']))
        if not years or (meta['title']=='The Clone Wars' and 'film' in label):
            years.append(meta['year'])
        release=str(min(years)) if min(years)==max(years) else f'{min(years)}–{max(years)}'
        notes=re.findall(r'\(([^)]+)\)',label)
        display=re.sub(r'\s*\([^)]*\)','',label).strip().rstrip('.')
        # A specific time-travel clip must not inherit the film's main-era position.
        story=None if '2012 escape' in label else meta['story']
        era='Endgame’s branching-time scene' if '2012 escape' in label else meta['era']
        key=hashlib.sha1(label.encode()).hexdigest()[:12]
        result.append(dict(key=key,label=display,notes=notes,release=release,year=min(years),
                           story=story,era=era,format=meta['format'],branch=meta.get('branch','Main continuity'),index=index))
    return result


def render_route(route, titles):
    rid=route_id(route)
    events=steps(route,titles)
    timeline=''
    for e in events:
        notes=''
        if e['notes']:
            notes='<details class="watch-step-notes"><summary>Selection notes</summary>'+''.join(f'<p>{esc(n)}</p>' for n in e['notes'])+'</details>'
        story='' if e['story'] is None else str(e['story'])
        branch=f' · {esc(e["branch"])}' if e['branch']!='Main continuity' else ''
        timeline+=f'''<li class="watch-step" id="{rid}-{e['key']}" data-key="{e['key']}" data-guide="{e['index']}" data-release="{e['year']}" data-story="{story}"><span class="watch-node" aria-hidden="true">{e['index']+1:02}</span><div class="watch-step-copy"><p class="watch-meta">{esc(e['format'])} · <time>{esc(e['release'])}</time>{branch}</p><h3>{esc(e['label'])}</h3><p class="watch-era">{esc(e['era'])}</p>{notes}<label class="watch-complete" hidden><input type="checkbox" data-watched="{e['key']}"> I’ve watched this selection</label></div></li>'''
    extras=''.join(f'<li>{esc(note)}</li>' for note in route['extras'])
    first=f'<p class="watch-start"><strong>Begin here:</strong> {esc(events[0]["label"])}. Follow the recommended order for this character; other franchise routes are optional.</p>' if events else f'<p class="watch-start">{esc(route["core"][0])}</p>'
    progress=f'''<div class="watch-progress" hidden><label for="progress-{rid}">Your core route <span class="watch-count">0 / {len(events)} steps</span></label><progress id="progress-{rid}" value="0" max="{len(events)}">0 of {len(events)}</progress><p class="watch-next"></p><div class="watch-actions"><button type="button" data-next>Jump to next unwatched</button><button type="button" data-reset>Reset this route</button></div></div>''' if events else ''
    routebody=f'<ol class="watch-timeline">{timeline}</ol><p class="watch-empty" hidden>Every core selection is marked watched. Show completed steps to revisit the timeline, or explore the optional detours.</p>' if events else ''
    return f'''<details class="watch-route" id="{rid}" data-world="{route['universe']}" data-name="{esc(route['name'],quote=True)}"><summary>{esc(route['name'])} <span>{len(events)} core selections / {route['universe']}</span></summary><div class="watch-route-body"><h2 tabindex="-1">{esc(route['name'])}</h2>{first}{progress}<p class="watch-order-note" role="status" aria-live="polite"></p>{routebody}<details class="watch-detours"><summary>Optional detours and context <span>{len(route['extras'])} notes</span></summary><p>Choose these when their subject interests you. Existing guide notes discuss broad character turns and may reveal connections.</p><ul>{extras}</ul></details></div></details>'''


def main():
    from build_game_guides import render as render_lore
    routes=[r for r in json.loads((ROOT/'content/guides.json').read_text()) if r['medium']=='screen']
    metadata=json.loads((ROOT/'content/guides/screen-titles.json').read_text())
    ids=[route_id(r) for r in routes]
    assert len(set(ids))==len(ids), 'Duplicate screen route ID'
    options=''
    for world in ('MCU','Star Wars'):
        options+=f'<optgroup label="{world}">'+''.join(f'<option value="{route_id(r)}">{esc(r["name"])}</option>' for r in routes if r['universe']==world)+'</optgroup>'
    mast=re.search(r'<header class="mast">.*?</header>',(ROOT/'guides/index.html').read_text(),re.S)[0]
    mast=mast.replace('href="../','href="../../').replace('href="./"','href="../"').replace(' aria-current="page"','')
    bodies='\n'.join(render_route(r,metadata['titles']) for r in routes)
    sources=''.join(f'<li><a href="{esc(url,quote=True)}">{esc(label)}</a></li>' for label,url in metadata['sources'])
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#171c28"><title>Interactive TV &amp; movie character timelines | Fourth Frame</title><meta name="description" content="Follow MCU and Star Wars characters through manageable viewing routes. Compare viewing orders, track watched selections, and choose optional detours."><link rel="canonical" href="{BASE}guides/screen/"><meta property="og:type" content="website"><meta property="og:site_name" content="Fourth Frame"><meta property="og:title" content="TV &amp; movie character timelines"><meta property="og:description" content="Choose a character. Find your next watch."><meta property="og:url" content="{BASE}guides/screen/"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../../assets/style.css"><link rel="stylesheet" href="../../assets/screen-guides.css"><script defer src="../../assets/screen-guides.js"></script><script defer src="../../assets/analytics.js"></script></head><body><a class="skip" href="#main">Skip to content</a>{mast}<main class="shell screen-guides" id="main"><header class="watch-heading"><a href="../">All guides</a><p class="eyebrow">Screen / {len(routes)} character routes</p><h1>A story worth following.<br>One watch at a time.</h1><p>Choose a character, see the essential path, and leave room for curiosity. You don’t need to finish every film and show in the universe.</p></header><section class="watch-controls" aria-label="Choose and explore a viewing route" hidden><label>World<select id="watch-world"><option value="all">All screen worlds</option><option>MCU</option><option>Star Wars</option></select></label><label class="watch-character-control">Character or group<select id="watch-character">{options}</select></label><label>Timeline view<select id="watch-order"><option value="guide">Recommended viewing order</option><option value="release">Release / season-debut order</option><option value="story">Broad story-era order</option></select></label><label class="watch-toggle"><input type="checkbox" id="watch-hide-completed"> Hide watched selections</label><button type="button" id="watch-share">Copy this route’s link</button><p id="watch-status" role="status" aria-live="polite"></p></section><p class="watch-storage" hidden>Watch marks stay in this browser. They count selections, not viewing hours, and never change the spoiler notes or someone else’s shared link.</p><noscript><p>Open a character below to read their timeline. Sorting and progress tracking need JavaScript.</p></noscript><div id="watch-routes">{bodies}</div><section class="watch-scope"><h2>How to read these timelines</h2><p>Recommended order is Fourth Frame’s existing character-first route. Release comparisons use a film or special’s release year and selected seasons’ debut years; episode dates within a season may differ. A combined selection stays together and sorts by its earliest debut.</p><p>Story-era order is a broad comparison, not a scene-by-scene chronology or a new first-viewing recommendation. Ties preserve the guide’s order. Anthologies, independent stories, and separate Marvel branches without a single placement appear last. The Clone Wars’ final arc overlaps Episode III; Andor and Rebels overlap; time travel and credits scenes can reach outside a title’s main era.</p><p>Viewing selections retain the 28 September 2026 edition’s scope. Timeline metadata reviewed {metadata['reviewed']}. No new upcoming titles are added. Cal Kestis’s main adventures are in the Jedi games rather than films or television.</p><details><summary>Reference material (may contain spoilers)</summary><ul>{sources}</ul></details></section><dialog id="watch-reset-dialog" aria-labelledby="watch-reset-title"><form method="dialog"><h2 id="watch-reset-title">Reset this route?</h2><p id="watch-reset-text"></p><div class="watch-actions"><button value="cancel" autofocus>Keep my progress</button><button value="reset" id="watch-confirm-reset">Clear this route’s marks</button></div></form></dialog></main><footer class="footer shell"><span>Fourth Frame · Writing by Peter D’Souza</span><a href="#main">Back to top ↑</a></footer></body></html>'''
    out=ROOT/'guides/screen/index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page)
    lore=json.loads((ROOT/'content/guides/mcu-lore.json').read_text())
    lore_out=ROOT/'guides/mcu/index.html'
    lore_out.parent.mkdir(exist_ok=True)
    lore_out.write_text(render_lore(lore))
    index=ROOT/'search-index.json'
    rows=[r for r in json.loads(index.read_text()) if r['url'] not in ('guides/screen/','guides/mcu/')]
    rows.append(dict(title='TV & movie character timelines',url='guides/screen/',type='Guide',description='Follow MCU and Star Wars characters, compare viewing orders, and track your next watch.',tags=['Guides','MCU','Star Wars','TV','Movies'],body=' '.join(r['name'] for r in routes)))
    rows.append(dict(title='MCU: lore and where to start',url='guides/mcu/',type='Guide',description=lore['description'],tags=['Guides','MCU','Lore'],body=' '.join([lore['intro'],lore['recommendation']]+[c['name'] for c in lore['characters']])))
    index.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    namespace='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',namespace)
    sitemap=ET.parse(ROOT/'sitemap.xml')
    for url in (BASE+'guides/screen/',BASE+'guides/mcu/'):
        if url not in {e.text for e in sitemap.findall(f'.//{{{namespace}}}loc')}:
            ET.SubElement(ET.SubElement(sitemap.getroot(),f'{{{namespace}}}url'),f'{{{namespace}}}loc').text=url
    sitemap.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    print(f'Built screen timelines for {len(routes)} existing character routes.')


if __name__=='__main__':
    main()
