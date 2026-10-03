(() => {
  const root = document.querySelector('.game-guide');
  if (!root) return;
  const data = JSON.parse(document.getElementById('game-guide-data').textContent);
  const limit = document.getElementById('spoiler-limit');
  const order = document.getElementById('timeline-order');
  const character = document.getElementById('timeline-character');
  const mainOnly = document.getElementById('recommended-only');
  const timeline = document.getElementById('story-timeline');
  const events = [...timeline.querySelectorAll('.timeline-event')];
  const spoilers = [...root.querySelectorAll('[data-spoiler]')];
  const status = document.getElementById('timeline-status');
  const dialog = document.getElementById('recap-dialog');
  const recapSets = {
    campaign: ['wc1', 'wc2', 'portal'],
    modern: ['legion', 'bfa', 'shadow', 'dragon', 'warwithin'],
    saga: ['legion', 'bfa', 'shadow', 'dragon'],
    classic: ['wc3', 'frozen'],
    crew: ['me1']
  };
  function update() {
    const allowed = new Set(data.milestones.find(m => m.value === limit.value).unlocks);
    spoilers.forEach(node => {
      node.hidden = !allowed.has(node.dataset.spoiler);
      if (node.hidden && node.tagName === 'DETAILS') node.open = false;
    });
    events.forEach(event => {
      const note = event.querySelector('.locked-note');
      if (note) note.hidden = allowed.has(event.dataset.event);
    });
    root.querySelectorAll('.character-outcomes').forEach(box => {
      const any = [...box.querySelectorAll('[data-spoiler]')].some(node => !node.hidden);
      box.querySelector('.character-locked').hidden = any;
      if (!any) box.open = false;
    });
    let visible = 0;
    [...events].sort((a,b) => Number(a.dataset[order.value === 'story' ? 'story' : 'release']) - Number(b.dataset[order.value === 'story' ? 'story' : 'release'])).forEach(event => {
      const relevant = character.value === 'all' || event.dataset.characters.split(' ').includes(character.value);
      event.hidden = !relevant || (mainOnly.checked && event.dataset.optional === 'true');
      if (!event.hidden) visible++;
      timeline.append(event);
    });
    status.textContent = `${visible} ${visible === 1 ? 'entry' : 'entries'} shown. ${limit.selectedOptions[0].textContent}.`;
    document.getElementById('timeline-empty').hidden = visible > 0;
  }
  [limit,order,character,mainOnly].forEach(control => control.addEventListener('change',update));
  root.querySelectorAll('[data-follow]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click',() => {
      character.value = button.dataset.follow;
      mainOnly.checked = false;
      update();
      character.focus({preventScroll:true});
      document.getElementById('timeline').scrollIntoView();
    });
  });
  root.querySelectorAll('[data-entry]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click',() => {
      const entry = data.entries.find(e => e.id === button.dataset.entry);
      limit.value = entry.unlock;
      update();
      document.getElementById('recap-title').textContent = `Before ${entry.title}`;
      document.getElementById('recap-intro').textContent = 'Earlier-story spoilers are now allowed for this starting point. Change the spoiler setting back to “I’m new” whenever you want to hide them.';
      const body = document.getElementById('recap-body');
      body.replaceChildren();
      const need = document.createElement('p');
      need.textContent = entry.need;
      body.append(need);
      (recapSets[entry.id] || []).forEach(id => {
        const event = document.getElementById(`event-${id}`);
        const heading = document.createElement('h3');
        heading.textContent = event.querySelector('h3').textContent;
        const text = document.createElement('p');
        text.textContent = event.querySelector('.story-spoiler p').textContent;
        body.append(heading,text);
      });
      dialog.showModal();
    });
  });
  document.getElementById('recap-close').addEventListener('click',() => dialog.close());
  // Initialise from scratch on each visit; shared links never silently unlock spoilers.
  limit.value = 'none';
  update();
  document.querySelector('.timeline-controls').hidden = false;
  // Character links may target an event excluded by the current filters.
  root.querySelectorAll('a[href^="#event-"]').forEach(link => link.addEventListener('click',() => {
    character.value = 'all';
    mainOnly.checked = false;
    update();
  }));
})();
