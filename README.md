# Fourth Frame

A dependency-free editorial portfolio for GitHub Pages. The homepage groups four long reads and two lists. The Halo, Mass Effect and Warcraft articles are editable drafts; review their wording, first-person recollections and factual claims before merging or presenting them as final published pieces.

## Repository and Pages

Target repository: `git@github.com:peterdsouza247/4thframe.git`.

The site assumes GitHub Pages serves the `main` branch from the repository root at `https://peterdsouza247.github.io/4thframe/`. In the repository's **Settings → Pages**, select **Deploy from a branch**, `main`, `/ (root)`. If Pages uses a different address, update every canonical and `og:url` tag, the JSON-LD `mainEntityOfPage` values, `robots.txt`, and `sitemap.xml`.

No build step is needed. The committed `.nojekyll` file tells Pages to serve the static files directly. To preview locally, run `python3 -m http.server 8000` in this directory and open `http://localhost:8000`.

## Editing articles

- Halo article: `stories/halo-starting-over/index.html`
- Mass Effect article: `stories/mass-effect-revisited/index.html`
- Warcraft III heroes article: `stories/warcraft-iii-heroes/index.html`
- Warcraft III campaigns article: `stories/replay-warcraft-iii-campaigns/index.html`
- Vampire list: `stories/vampires-in-gaming/index.html`
- Wolverine list: `stories/wolverine-storylines/index.html`
- Homepage cards and order: `index.html`
- Shared layout and colors: `assets/style.css`
- Image sourcing and rights log: `IMAGE-RIGHTS.md`

To add an article, create a `stories/<slug>/index.html` page and link its card in the matching Long reads or Lists section of `index.html`. Give each page a unique `<title>`, description, H1, canonical URL, Open Graph fields, byline, useful headings, and accurate Article structured data. Add its URL to `sitemap.xml`. Add publication and modification dates only when they are known.

The site uses a magazine-inspired masthead, warm paper and ink palette, and original CSS illustrations for its story covers. It currently has no licensed game imagery or social preview image. Add rights-cleared artwork and `og:image` later if desired.
