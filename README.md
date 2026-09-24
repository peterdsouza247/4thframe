# Fourth Frame

A dependency-free editorial portfolio for GitHub Pages. The working publication name is **Fourth Frame**. The first two article pages are editable drafts, reconstructed from earlier conversations rather than copies of the original article drafts. Review their wording and factual claims before presenting them as final published pieces.

## Repository and Pages

Target repository: `git@github.com:peterdsouza247/4thframe.git`.

The site assumes GitHub Pages serves the `main` branch from the repository root at `https://peterdsouza247.github.io/4thframe/`. In the repository's **Settings → Pages**, select **Deploy from a branch**, `main`, `/ (root)`. If Pages uses a different address, update every canonical and `og:url` tag, the JSON-LD `mainEntityOfPage` values, `robots.txt`, and `sitemap.xml`.

No build step is needed. The committed `.nojekyll` file tells Pages to serve the static files directly. To preview locally, run `python3 -m http.server 8000` in this directory and open `http://localhost:8000`.

## Editing articles

- Halo article: `stories/halo-starting-over/index.html`
- Mass Effect article: `stories/mass-effect-revisited/index.html`
- Homepage cards and order: `index.html`
- Shared layout and colors: `assets/style.css`

The homepage has two unlinked slots for future listicles. When those articles are ready, add a `stories/<slug>/index.html` page for each, then link its homepage card. Give each page a unique `<title>`, description, H1, canonical URL, Open Graph fields, byline, useful headings, and accurate Article structured data. Add its URL to `sitemap.xml`. Add publication and modification dates only when they are known. Do not add placeholder article pages to the sitemap.

The site uses a typographic identity and CSS treatment; it currently has no licensed game imagery or social preview image. Add rights-cleared artwork and `og:image` later if desired.
