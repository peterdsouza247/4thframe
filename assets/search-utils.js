(() => {
  function normalize(value) {
    return String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim().replace(/\s+/g, ' ');
  }
  const compact = value => normalize(value).replace(/\s/g, '');
  function matches(text, query) {
    const haystack = normalize(text);
    const words = normalize(query).split(' ').filter(Boolean);
    if (!words.length) return true;
    const joined = haystack.replace(/\s/g, '');
    return words.every(word => haystack.includes(word) || joined.includes(word));
  }

  function suggestions(input, list, getChoices, onChoose) {
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-controls', list.id);
    input.setAttribute('aria-expanded', 'false');
    list.setAttribute('role', 'listbox');
    let active = -1;
    let choices = [];
    const close = () => {
      list.replaceChildren();
      list.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
      active = -1;
    };
    function highlight(index) {
      active = index;
      [...list.children].forEach((item, i) => item.setAttribute('aria-selected', String(i === index)));
      if (index >= 0) input.setAttribute('aria-activedescendant', list.children[index].id);
      else input.removeAttribute('aria-activedescendant');
    }
    function choose(index) {
      input.value = choices[index].value;
      close();
      onChoose();
      input.focus();
    }
    function refresh() {
      const term = input.value.trim();
      close();
      if (compact(term).length < 2) return;
      choices = getChoices().filter(item => matches(item.label + ' ' + item.value, term))
        .sort((a, b) => {
          const rank = item => compact(item.value).startsWith(compact(term)) ? 0 : 1;
          return rank(a) - rank(b) || a.label.localeCompare(b.label);
        }).slice(0, 6);
      if (!choices.length) return;
      choices.forEach((item, index) => {
        const option = document.createElement('div');
        option.id = `${list.id}-${index}`;
        option.setAttribute('role', 'option');
        option.setAttribute('aria-selected', 'false');
        option.textContent = item.label;
        option.addEventListener('mousedown', event => event.preventDefault());
        option.addEventListener('click', () => choose(index));
        list.append(option);
      });
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }
    input.addEventListener('input', refresh);
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape') { close(); return; }
      if (list.hidden) return;
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        highlight(active < 0 ? (event.key === 'ArrowDown' ? 0 : choices.length - 1) :
          (active + (event.key === 'ArrowDown' ? 1 : choices.length - 1)) % choices.length);
      } else if (event.key === 'Enter' && active >= 0) {
        event.preventDefault();
        choose(active);
      }
    });
    input.addEventListener('blur', () => setTimeout(close, 120));
    document.addEventListener('pointerdown', event => {
      if (event.target !== input && !list.contains(event.target)) close();
    });
    return { refresh, close };
  }
  window.FourthFrameSearch = { normalize, compact, matches, suggestions };
})();
