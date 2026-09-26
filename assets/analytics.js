/* Set the URL from your GoatCounter dashboard once; every page loads this file. */
const GOATCOUNTER_URL = '';

/* Set true after enabling public visitor counts in GoatCounter site settings. */
const SHOW_PUBLIC_COUNTS = false;

(() => {
  if (!GOATCOUNTER_URL) return;

  if (!/^https:\/\/[a-z0-9-]+\.goatcounter\.com\/count$/.test(GOATCOUNTER_URL)) {
    console.warn('Fourth Frame: use a GoatCounter URL like https://yourcode.goatcounter.com/count');
    return;
  }

  const script = document.createElement('script');
  script.src = 'https://gc.zgo.at/count.js';
  script.async = true;
  script.dataset.goatcounter = GOATCOUNTER_URL;
  script.onload = () => {
    if (SHOW_PUBLIC_COUNTS && document.querySelector('.article-views')) {
      window.goatcounter.visit_count({ append: '.article-views', type: 'html' });
    }
  };
  document.head.appendChild(script);
})();
