# Fourth Frame

A dependency-free editorial portfolio for GitHub Pages. The homepage groups long reads and lists. Articles are editable drafts; review their wording, first-person recollections and factual claims before presenting them as final published pieces.

## Repository and Pages

Target repository: `git@github.com:peterdsouza247/4thframe.git`.

The site assumes GitHub Pages serves the `main` branch from the repository root at `https://peterdsouza247.github.io/4thframe/`. In the repository's **Settings → Pages**, select **Deploy from a branch**, `main`, `/ (root)`. If Pages uses a different address, update every canonical and `og:url` tag, the JSON-LD `mainEntityOfPage` values, `robots.txt`, and `sitemap.xml`.

No build step is needed. The committed `.nojekyll` file tells Pages to serve the static files directly. To preview locally, run `python3 -m http.server 8000` in this directory and open `http://localhost:8000`.

## Editing articles

Article files (updated by `scripts/add_article.py`):

<!-- article-files:start -->
- telltales-batman-reinvention: `stories/telltales-batman-reinvention/index.html`
- halo-starting-over: `stories/halo-starting-over/index.html`
- mass-effect-revisited: `stories/mass-effect-revisited/index.html`
- warcraft-iii-heroes: `stories/warcraft-iii-heroes/index.html`
- replay-warcraft-iii-campaigns: `stories/replay-warcraft-iii-campaigns/index.html`
- vampires-in-gaming: `stories/vampires-in-gaming/index.html`
- wolverine-storylines: `stories/wolverine-storylines/index.html`
- best-j2me-games: `stories/best-j2me-games/index.html`
- j2me-mobile-gaming-history: `stories/j2me-mobile-gaming-history/index.html`
- underrated-nes-games: `stories/underrated-nes-games/index.html`
- consoles-deserved-better: `stories/consoles-deserved-better/index.html`
- cancelled-games-masterpieces: `stories/cancelled-games-masterpieces/index.html`
- when-the-world-stopped-being-the-point: `stories/when-the-world-stopped-being-the-point/index.html`
- what-made-elden-ring-great: `stories/what-made-elden-ring-great/index.html`
- mmos-that-transported-us: `stories/mmos-that-transported-us/index.html`
- master-one-way-or-mix: `stories/master-one-way-or-mix/index.html`
- when-the-fight-stopped-moving: `stories/when-the-fight-stopped-moving/index.html`
- from-browser-duel-to-full-game: `stories/from-browser-duel-to-full-game/index.html`
<!-- article-files:end -->
- Homepage cards and order: `index.html`
- Shared layout and colors: `assets/style.css`
- Article tags and related-story links: `content/articles.json`
- Search interface: `search/index.html` and `assets/search.js`
- Generated search data: `search-index.json`
- Image sourcing and rights log: `IMAGE-RIGHTS.md`

To add an article, copy [`ARTICLE-TEMPLATE.md`](ARTICLE-TEMPLATE.md) to a new `.md` file, replace its sample copy and metadata, then run `python3 scripts/add_article.py path/to/article.md --dry-run` followed by `python3 scripts/add_article.py path/to/article.md`. The script rejects duplicate slugs and broken related-story references, creates the article page, adds a homepage card or list row, updates `content/articles.json`, `sitemap.xml` and the article-file list above, then refreshes search data, topic links, related stories, social tags and Article JSON-LD. Commit the new HTML and generated files together. The `.md` draft can also be committed if you want an editable source; the publisher does not require it to be in the repository.

The metadata header accepts `title`, `slug`, `type` (`Long read` or `List`), `description`, `summary`, `category`, `tags`, and optional `related`, `cover_label`, `art`, and `published`. Tags and related slugs use JSON arrays of double-quoted strings. For a list, choose `type: "List"`; the script places it in Lists. Omit `published` until you know the actual publication date. Body Markdown supports paragraphs, `##`/`###` headings, bold, italics, inline code, links, simple lists and blockquotes. Separate lists and headings with blank lines. Raw HTML is escaped. For images, place the file in `assets/images/`, log its use in `IMAGE-RIGHTS.md`, and use a standalone line like `![Alt text](../../assets/images/example.jpg "Creator / source / licence")`. The script checks that the file exists and adds a caption. For richer Markdown, edit the generated HTML before publishing.

After editing an existing article's HTML or its tags in `content/articles.json`, run `python3 scripts/build_content.py` to refresh search and article metadata. Search indexes full article text as well as titles, descriptions and tags. Changing a title or description in existing HTML still requires updating its other static `<title>`/Open Graph fields and homepage card manually. The publishing command automates these for new pages.

Give each article a unique `<title>`, description, H1, canonical URL and useful headings. Add its URL to `sitemap.xml`. Add publication and modification dates only when they are known. Search results are marked `noindex` to avoid indexing query pages; articles remain discoverable through ordinary HTML links and the sitemap. Tags are for readers and on-site search; they do not guarantee search-engine ranking.

The site uses a magazine-inspired masthead, warm paper and ink palette, and original CSS illustrations for its story covers. It currently has no licensed game imagery or social preview image. To add one, follow the rights and `<figure>` instructions in `IMAGE-RIGHTS.md`, then add an `og:image` only when the same permission covers sharing a social preview.

For optional private page analytics and public article view counters, see [`GOATCOUNTER.md`](GOATCOUNTER.md). Enter the counting URL once in `assets/analytics.js`; all pages already load the dormant template.

## Development Journal

The three *Masters of the Way* draft entries have editable Markdown in
`content/journal/`. Review the first-person wording and playtest claims before
merging this change. Their generated pages live in `stories/`, their cards in
the homepage Journal section, and their full text in site search.

After editing a draft, run for example:

```bash
python3 scripts/update_journal.py content/journal/when-the-fight-stopped-moving.md
```

The command regenerates its page, homepage card, tags, related links and search
index. For a new entry, use `ARTICLE-TEMPLATE.md` with `type: "Journal"`, save
it in `content/journal/`, then use `scripts/add_article.py` as above. Keep the
Markdown source with the generated HTML. The journal describes Peter's own
game and is identified as such on the homepage.

## Character guides

The Guides section lives at `guides/`. Edit `content/guides/screen.md` and `content/guides/comics.md`, then run `python3 scripts/build_guides.py`. Commit the source files, generated `content/guides.json`, and `guides/index.html` together. Each character is a three-column Markdown table row (`Character | Core | Extras`); separate core steps with `→` and optional notes with semicolons. The builder preserves the full wording as searchable text, produces static HTML cards for indexing and no-JavaScript reading, and checks that entries were parsed. The filter/sort interaction is in `assets/guides.js`. Update the edition date and scope notes when adding new releases or comics.

Search suggestions and punctuation-tolerant matching are shared by the article archive and character guides in `assets/search-utils.js`. Search matches forms such as `Spider-Man`, `Spider Man` and `spiderman`; suggestions use article titles/topics or character names/route steps.
