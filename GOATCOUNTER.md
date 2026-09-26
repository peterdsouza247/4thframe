# GoatCounter setup for Fourth Frame

The homepage, search page and every article already load `assets/analytics.js`. Tracking is inactive until you add your account URL. New pages created with `scripts/add_article.py` include the loader automatically.

1. Create a site at [GoatCounter](https://www.goatcounter.com/) and copy the counting URL shown in its setup instructions. It looks like `https://yourcode.goatcounter.com/count`.
2. Open `assets/analytics.js`. Replace the empty value in `const GOATCOUNTER_URL = '';` with your exact counting URL. **Keep `/count` at the end.** This is the only location to edit for ordinary analytics; do not put the URL in every HTML page.
3. Commit and deploy the change. Open a live article, then check your GoatCounter dashboard. Local previews are deliberately not counted by default. An ad blocker may prevent a test visit from appearing.

## Optional public article counters

The site's article bylines contain an empty `article-views` placeholder. To show counts to readers, first turn on **Allow adding visitor counts on your website** in GoatCounter's site settings. Then set `SHOW_PUBLIC_COUNTS = true` in `assets/analytics.js`. The public counts may take up to four hours to reflect new views. Keep the setting `false` if you only want private analytics. A public counter shows page views, which are different from unique readers.

GoatCounter is currently free for reasonable public usage. See its [getting started guide](https://www.goatcounter.com/help/start) and [visitor-counter documentation](https://www.goatcounter.com/help/visitor-counter) for current settings.

If you change this site's domain later, update the canonical URLs, sitemap and `BASE` in `scripts/add_article.py` along with the GoatCounter site domain settings. The analytics loader uses the canonical page URL supplied in the HTML, so keeping those URLs accurate matters.
