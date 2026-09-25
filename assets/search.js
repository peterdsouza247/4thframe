(() => {
  const input = document.querySelector("#search-input");
  const form = document.querySelector(".search-form");
  const filters = document.querySelector("#tag-filters");
  const count = document.querySelector("#search-count");
  const results = document.querySelector("#results");
  const params = new URLSearchParams(location.search);
  let selectedTag = params.get("tag") || "";
  let articles = [];

  const normalize = value => value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const occurrences = (text, term) => text.split(term).length - 1;

  function updateUrl() {
    const next = new URLSearchParams();
    if (input.value.trim()) next.set("q", input.value.trim());
    if (selectedTag) next.set("tag", selectedTag);
    history.replaceState(null, "", location.pathname + (next.size ? "?" + next : ""));
  }

  function addText(parent, tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    parent.append(node);
    return node;
  }

  function excerpt(article, terms) {
    if (!terms.length) return article.description;
    const body = article.body;
    const normalized = normalize(body);
    const matches = terms.map(term => normalized.indexOf(term)).filter(index => index >= 0);
    if (!matches.length) return article.description;
    const start = Math.max(0, Math.min(...matches) - 75);
    const end = Math.min(body.length, start + 210);
    return (start ? "…" : "") + body.slice(start, end).trim() + (end < body.length ? "…" : "");
  }

  function renderFilters() {
    const tags = [...new Set(articles.flatMap(article => article.tags))].sort((a, b) => a.localeCompare(b));
    filters.replaceChildren();
    for (const tag of ["All topics", ...tags]) {
      const button = addText(filters, "button", tag);
      button.type = "button";
      const value = tag === "All topics" ? "" : tag;
      button.setAttribute("aria-pressed", String(selectedTag === value));
      button.addEventListener("click", () => {
        selectedTag = value;
        updateUrl();
        renderFilters();
        renderResults();
      });
    }
  }

  function renderResults() {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    const matches = articles.map(article => {
      const title = normalize(article.title);
      const tags = normalize(article.tags.join(" "));
      const description = normalize(article.description);
      const body = normalize(article.body);
      const combined = title + " " + tags + " " + description + " " + body;
      if (selectedTag && !article.tags.includes(selectedTag)) return null;
      if (!terms.every(term => combined.includes(term))) return null;
      const score = terms.reduce((total, term) =>
        total + occurrences(title, term) * 8 + occurrences(tags, term) * 7 +
        occurrences(description, term) * 3 + Math.min(occurrences(body, term), 5), 0);
      return { article, score };
    }).filter(Boolean).sort((a, b) => b.score - a.score);

    results.replaceChildren();
    count.textContent = matches.length + (matches.length === 1 ? " story" : " stories") +
      (selectedTag ? " · " + selectedTag : "");
    if (!matches.length) {
      addText(results, "p", "No matches yet. Try a shorter phrase or another topic.", "empty-state");
      return;
    }
    for (const { article } of matches) {
      const card = document.createElement("article");
      card.className = "result";
      const main = document.createElement("div");
      addText(main, "span", article.tags.join(" · "), "result-tags");
      const heading = document.createElement("h2");
      const link = addText(heading, "a", article.title);
      link.href = "../" + article.url;
      main.append(heading);
      addText(main, "p", excerpt(article, terms));
      card.append(main);
      addText(card, "span", article.type, "meta");
      results.append(card);
    }
  }

  input.value = params.get("q") || "";
  form.addEventListener("submit", event => {
    event.preventDefault();
    updateUrl();
    renderResults();
  });
  input.addEventListener("input", () => {
    updateUrl();
    renderResults();
  });

  fetch("../search-index.json")
    .then(response => {
      if (!response.ok) throw new Error("Search index could not be loaded.");
      return response.json();
    })
    .then(data => {
      articles = data;
      if (!articles.some(article => article.tags.includes(selectedTag))) selectedTag = "";
      renderFilters();
      renderResults();
    })
    .catch(() => {
      count.textContent = "Search unavailable";
      results.replaceChildren();
      const message = addText(results, "p", "The search index could not load. Browse every story from the homepage.", "empty-state");
      const link = addText(message, "a", " View the homepage.");
      link.href = "../";
    });
})();
