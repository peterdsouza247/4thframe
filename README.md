# Fourth Frame

A dependency-free editorial portfolio for GitHub Pages. The homepage groups five long reads and two lists. The Halo, Mass Effect, Warcraft and Batman articles are editable drafts; review their wording, first-person recollections and factual claims before presenting them as final published pieces.

## Repository and Pages

Target repository: `git@github.com:peterdsouza247/4thframe.git`.

The site assumes GitHub Pages serves the `main` branch from the repository root at `https://peterdsouza247.github.io/4thframe/`. In the repository's **Settings → Pages**, select **Deploy from a branch**, `main`, `/ (root)`. If Pages uses a different address, update every canonical and `og:url` tag, the JSON-LD `mainEntityOfPage` values, `robots.txt`, and `sitemap.xml`.

No build step is needed. The committed `.nojekyll` file tells Pages to serve the static files directly. To preview locally, run `python3 -m http.server 8000` in this directory and open `http://localhost:8000`.

## Editing articles

- Halo article: `stories/halo-starting-over/index.html`
- Mass Effect article: `stories/mass-effect-revisited/index.html`
- Warcraft III heroes article: `stories/warcraft-iii-heroes/index.html`
- Warcraft III campaigns article: `stories/replay-warcraft-iii-campaigns/index.html`
- Telltale Batman article: `stories/telltales-batman-reinvention/index.html`
- Vampire list: `stories/vampires-in-gaming/index.html`
- Wolverine list: `stories/wolverine-storylines/index.html`
- Homepage cards and order: `index.html`
- Shared layout and colors: `assets/style.css`
- Article tags and related-story links: `content/articles.json`
- Search interface: `search/index.html` and `assets/search.js`
- Generated search data: `search-index.json`
- Image sourcing and rights log: `IMAGE-RIGHTS.md`

To add an article, create a `stories/<slug>/index.html` page and link its card in the matching Long reads or Lists section of `index.html`. Add its slug, type, tags and related articles to `content/articles.json`, then run `python3 scripts/build_content.py` and commit the updated `search-index.json` and pages. Search indexes the full article text along with titles, descriptions and tags. This command also updates the visible topic links, related-story links, social meta tags and Article JSON-LD on all story pages. Run it after editing any article's body or metadata so search stays current.

Give each article a unique `<title>`, description, H1, canonical URL and useful headings. Add its URL to `sitemap.xml`. Add publication and modification dates only when they are known. Search results are marked `noindex` to avoid indexing query pages; articles remain discoverable through ordinary HTML links and the sitemap. Tags are for readers and on-site search; they do not guarantee search-engine ranking.

The site uses a magazine-inspired masthead, warm paper and ink palette, and original CSS illustrations for its story covers. It currently has no licensed game imagery or social preview image. To add one, follow the rights and `<figure>` instructions in `IMAGE-RIGHTS.md`, then add an `og:image` only when the same permission covers sharing a social preview.
