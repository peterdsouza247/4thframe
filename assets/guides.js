(() => {
  const grid = document.getElementById('guide-grid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.guide-card')];
  const query = document.getElementById('guide-search');
  const sort = document.getElementById('guide-sort');
  const coreOnly = document.getElementById('core-only');
  const status = document.getElementById('guide-status');
  const empty = document.getElementById('guide-empty');
  let medium = 'all';
  let universe = 'all';

  function press(group, chosen) {
    group.querySelectorAll('button').forEach(button => {
      button.setAttribute('aria-pressed', String(button === chosen));
    });
  }

  function update() {
    const needle = query.value.trim().toLocaleLowerCase();
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
        (!needle || card.dataset.search.includes(needle));
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    grid.classList.toggle('core-only', coreOnly.checked);
    empty.hidden = visible > 0;
    status.textContent = `${visible} ${visible === 1 ? 'route' : 'routes'} shown${coreOnly.checked ? ' · core steps only' : ''}. Select a card to read its path.`;
  }

  document.querySelector('.guide-kind').addEventListener('click', event => {
    const button = event.target.closest('button[data-medium]');
    if (!button) return;
    medium = button.dataset.medium;
    press(event.currentTarget, button);
    update();
  });
  document.querySelector('.guide-filters').addEventListener('click', event => {
    const button = event.target.closest('button[data-universe]');
    if (!button) return;
    universe = button.dataset.universe;
    press(event.currentTarget, button);
    update();
  });
  query.addEventListener('input', update);
  sort.addEventListener('change', update);
  coreOnly.addEventListener('change', update);
  update();
})();
