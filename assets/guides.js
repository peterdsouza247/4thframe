(() => {
  const grid = document.getElementById('guide-grid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.guide-card')];
  const query = document.getElementById('guide-search');
  const sort = document.getElementById('guide-sort');
  const coreOnly = document.getElementById('core-only');
  const status = document.getElementById('guide-status');
  const empty = document.getElementById('guide-empty');
  const suggest = window.FourthFrameSearch;
  const suggestionList = document.getElementById('guide-suggestions');
  const worldGrid = document.getElementById('world-grid');
  const worldTiles = worldGrid ? [...worldGrid.querySelectorAll('.world-tile')] : [];
  const viewButtons = document.querySelector('.guide-view');
  let view = worldGrid ? 'worlds' : 'routes';
  let medium = 'all';
  let universe = 'all';

  function press(group, chosen) {
    group.querySelectorAll('button').forEach(button => {
      button.setAttribute('aria-pressed', String(button === chosen));
    });
  }

  function update() {
    const needle = query.value.trim();
    const ordered = cards.map((card, index) => ({ card, index }));
    if (sort.value !== 'editorial') ordered.sort((a, b) => {
      const byName = a.card.dataset.name.localeCompare(b.card.dataset.name);
      const byLength = Number(a.card.dataset.coreCount) - Number(b.card.dataset.coreCount);
      if (sort.value === 'name') return byName;
      return (sort.value === 'shortest' ? byLength : -byLength) || byName;
    });
    const fragment = document.createDocumentFragment();
    ordered.forEach(({card}) => fragment.append(card));
    grid.append(fragment);
    let visible = 0;
    cards.forEach(card => {
      const matches = (medium === 'all' || card.dataset.medium === medium) &&
        (universe === 'all' || card.dataset.universe === universe) &&
        suggest.matches(card.dataset.search, needle);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    grid.classList.toggle('core-only', coreOnly.checked);
    grid.hidden = view === 'worlds';
    let worlds = 0;
    worldTiles.forEach(tile => {
      tile.hidden = !(medium === 'all' || tile.dataset.medium === medium) || !(universe === 'all' || tile.dataset.world === universe);
      if (!tile.hidden) worlds++;
    });
    if (worldGrid) worldGrid.hidden = view !== 'worlds';
    viewButtons?.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.guideView===view)));
    document.querySelector('.guide-sort').hidden = view === 'worlds';
    document.querySelector('.guide-toggle').hidden = view === 'worlds';
    empty.hidden = view === 'worlds' ? worlds > 0 : visible > 0;
    status.textContent = view === 'worlds' ? `${worlds} worlds. Explore the lore or choose a starting point.` : `${visible} ${visible === 1 ? 'route' : 'routes'} shown${coreOnly.checked ? ' · core steps only in watch/read routes' : ''}. Choose a series or character to begin.`;
  }

  document.querySelector('.guide-kind').addEventListener('click', event => {
    const button = event.target.closest('button[data-medium]');
    if (!button) return;
    medium = button.dataset.medium;
    press(event.currentTarget, button);
    update();
  });
  document.getElementById('guide-universe').addEventListener('change', event => {
    universe = event.target.value;
    update();
  });
  query.addEventListener('input', () => { if(query.value.trim()) view='routes'; update(); });
  viewButtons?.addEventListener('click',event => {
    const button=event.target.closest('[data-guide-view]');if(!button)return;
    view=button.dataset.guideView;
    if(view==='worlds') {
      query.value='';universe='all';medium='all';document.getElementById('guide-universe').value='all';
      press(document.querySelector('.guide-kind'),document.querySelector('.guide-kind [data-medium="all"]'));
    }
    update();
  });
  worldGrid?.addEventListener('click',event => {
    const button=event.target.closest('[data-browse-world]');if(!button)return;
    universe=button.dataset.browseWorld;medium=button.dataset.browseMedium;view='routes';query.value='';
    document.getElementById('guide-universe').value=universe;
    press(document.querySelector('.guide-kind'),document.querySelector(`.guide-kind [data-medium="${medium}"]`));
    update();document.querySelector('.guide-controls').scrollIntoView({block:'start'});query.focus({preventScroll:true});
  });
  suggest.suggestions(query, suggestionList, () => {
    const eligible = cards.filter(card => (medium === 'all' || card.dataset.medium === medium) &&
      (universe === 'all' || card.dataset.universe === universe));
    const names = eligible.flatMap(card => {
      const full = card.querySelector('h3').textContent;
      const short = full.split('/').map(part => part.replace(/^MCU\s+/, '').trim());
      return [full, ...short.filter(part => part !== full)].map(value => ({
        label: value === full ? full : `${value} · ${full}`,
        value: value === full ? full : value
      }));
    });
    const titles = eligible.flatMap(card => [...card.querySelectorAll('ol li')].map(item => ({
      label: `${item.textContent} · ${card.querySelector('h3').textContent}`,
      value: item.textContent
    })));
    return [...names, ...titles];
  }, update);
  sort.addEventListener('change', update);
  coreOnly.addEventListener('change', update);
  update();
})();
