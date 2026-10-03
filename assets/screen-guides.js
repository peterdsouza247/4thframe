(() => {
  const root = document.querySelector('.screen-guides');
  if (!root) return;
  const routes = [...document.querySelectorAll('.watch-route')];
  const world = document.getElementById('watch-world');
  const character = document.getElementById('watch-character');
  const order = document.getElementById('watch-order');
  const hideWatched = document.getElementById('watch-hide-completed');
  const status = document.getElementById('watch-status');
  const dialog = document.getElementById('watch-reset-dialog');
  const storageNote = document.querySelector('.watch-storage');
  const persistentStorageNote = storageNote.textContent;
  const storageKey = 'FourthFrame:watch-progress:v1';
  let watched = {};
  let storageAvailable = true;
  let selected;
  let pendingReset;
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '{}');
    if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
      routes.forEach(route => {
        const valid = new Set([...route.querySelectorAll('[data-watched]')].map(input => input.dataset.watched));
        watched[route.id] = Array.isArray(saved[route.id]) ? saved[route.id].filter(key => valid.has(key)) : [];
      });
    }
  } catch { storageAvailable = false; }

  function save() {
    try { localStorage.setItem(storageKey, JSON.stringify(watched)); storageAvailable = true; }
    catch { storageAvailable = false; }
    describeStorage();
  }
  function describeStorage() {
    storageNote.hidden = false;
    storageNote.textContent = storageAvailable ? persistentStorageNote : 'Browser storage is unavailable. Watch marks are kept for this visit only.';
  }
  function filterCharacters() {
    [...character.options].forEach(option => {
      const route = document.getElementById(option.value);
      option.hidden = option.disabled = world.value !== 'all' && route.dataset.world !== world.value;
    });
    [...character.querySelectorAll('optgroup')].forEach(group => { group.hidden = world.value !== 'all' && group.label !== world.value; });
  }
  function update() {
    const nodes = [...selected.querySelectorAll('.watch-step')];
    const done = new Set(watched[selected.id] || []);
    const recommended = [...nodes].sort((a,b) => Number(a.dataset.guide)-Number(b.dataset.guide));
    const ordered = [...nodes].sort((a,b) => {
      if (order.value === 'guide') return Number(a.dataset.guide)-Number(b.dataset.guide);
      const value = node => order.value === 'story' && node.dataset.story === '' ? Infinity : Number(node.dataset[order.value]);
      const left=value(a), right=value(b);
      return (left === right ? 0 : left-right) || Number(a.dataset.guide)-Number(b.dataset.guide);
    });
    ordered.forEach(node => {
      const complete = done.has(node.dataset.key);
      node.querySelector('[data-watched]').checked = complete;
      node.classList.toggle('is-watched', complete);
      node.hidden = hideWatched.checked && complete;
      selected.querySelector('.watch-timeline').append(node);
    });
    const next = recommended.find(node => !done.has(node.dataset.key));
    const count = recommended.filter(node => done.has(node.dataset.key)).length;
    const progress = selected.querySelector('progress');
    if (progress) {
      progress.value = count;
      progress.textContent = `${count} of ${nodes.length}`;
      selected.querySelector('.watch-count').textContent = `${count} / ${nodes.length} steps`;
      selected.querySelector('.watch-next').textContent = next ? `Next in the recommended route: ${next.querySelector('h3').textContent}` : 'You’ve marked every core selection watched. Optional detours are yours to choose.';
      selected.querySelector('[data-next]').disabled = !next;
      selected.querySelector('.watch-empty').hidden = !(hideWatched.checked && !next);
    }
    const notes = {
      guide: 'Recommended viewing order follows this character’s existing guide. The numbered nodes always refer to these original steps.',
      release: 'Comparison view: sorted by release year or the earliest selected season’s debut. Same-year ties keep the guide’s order; combined selections remain together. Return to recommended order for the suggested first viewing.',
      story: 'Comparison view: broad eras, with the guide’s order preserved inside each era. Overlapping series are not split. Multiple-era stories and separate branches without one placement appear last. This is not a spoiler-preserving first-viewing order.'
    };
    selected.querySelector('.watch-order-note').textContent = nodes.length ? notes[order.value] : 'This character has no film or television viewing route in this guide.';
    status.textContent = `${selected.dataset.name}: ${nodes.length} core ${nodes.length === 1 ? 'selection' : 'selections'}, ${count} marked watched.`;
  }
  function choose(id, updateLink = true) {
    selected = routes.find(route => route.id === id) || routes[0];
    if (world.value !== 'all' && world.value !== selected.dataset.world) world.value = selected.dataset.world;
    filterCharacters();
    character.value = selected.id;
    routes.forEach(route => { route.hidden = route !== selected; route.open = route === selected; });
    order.value = 'guide';
    if (updateLink) history.replaceState(null, '', `#${selected.id}`);
    update();
  }
  character.addEventListener('change', () => choose(character.value));
  world.addEventListener('change', () => {
    filterCharacters();
    const eligible = [...character.options].filter(option => !option.disabled);
    choose(eligible.some(option => option.value === selected.id) ? selected.id : eligible[0].value);
  });
  [order,hideWatched].forEach(control => control.addEventListener('change', update));
  routes.forEach(route => {
    route.querySelectorAll('.watch-complete,.watch-progress').forEach(node => { node.hidden = false; });
    route.addEventListener('change', event => {
      if (!event.target.matches('[data-watched]')) return;
      watched[route.id] = [...route.querySelectorAll('[data-watched]:checked')].map(input => input.dataset.watched);
      save();
      update();
    });
    route.querySelector('[data-next]')?.addEventListener('click', () => {
      const done = new Set(watched[route.id] || []);
      const next = [...route.querySelectorAll('.watch-step')].sort((a,b) => Number(a.dataset.guide)-Number(b.dataset.guide)).find(node => !done.has(node.dataset.key));
      if (next) { next.scrollIntoView({block:'center'}); next.querySelector('input').focus({preventScroll:true}); }
    });
    const reset = route.querySelector('[data-reset]');
    if (reset) {
      reset.hidden = typeof dialog.showModal !== 'function';
      reset.addEventListener('click', () => {
        pendingReset = route.id;
        dialog.returnValue = 'cancel';
        document.getElementById('watch-reset-text').textContent = `Clear the watch marks for ${route.dataset.name}? Other character routes keep their progress.`;
        dialog.showModal();
      });
    }
  });
  dialog.addEventListener('close', () => {
    if (dialog.returnValue === 'reset' && pendingReset) { watched[pendingReset] = []; save(); update(); }
    pendingReset = null;
  });
  document.getElementById('watch-share').addEventListener('click', async () => {
    const url = `${location.origin}${location.pathname}#${selected.id}`;
    try { await navigator.clipboard.writeText(url); status.textContent = 'Route link copied. Watch progress stays private to this browser.'; }
    catch {
      let input=document.getElementById('watch-copy-link');
      if (!input) {
        const label=document.createElement('label');label.textContent='Copy this route link';
        input=document.createElement('input');input.id='watch-copy-link';input.type='url';input.readOnly=true;
        label.append(input);document.querySelector('.watch-controls').append(label);
      }
      input.value=url;input.focus();input.select();
      status.textContent='Select and copy the route link above. Watch progress is not included.';
    }
  });
  window.addEventListener('hashchange', () => choose(location.hash.slice(1),false));
  root.classList.add('enhanced');
  document.querySelector('.watch-controls').hidden = false;
  describeStorage();
  choose(location.hash.slice(1),false);
})();
