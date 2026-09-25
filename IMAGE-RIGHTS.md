# Image rights checklist for Fourth Frame

This is a practical editorial workflow, not legal advice. Keep one row in the asset log below for every external image published on the site.

## How to add an image

1. **Find the original source and permission terms.** Prefer an official press kit that expressly allows editorial reuse, an image you have licensed, or your own image. For a game screenshot you capture, check the publisher's current game-content rules and whether the particular use fits them. An image on a press release or a search result is not automatically licensed for reuse.
2. **Record the rights details before uploading.** Note the creator/copyright holder, original URL, exact licence or permission, required credit text, any modification limits, and the date checked in the log below. Keep a copy of permission terms.
3. **Prepare the file.** Export a reasonably sized WebP/JPEG for a photo or screenshot, or PNG where transparency or text needs it. Give it a descriptive filename such as `telltale-batman-john-doe.webp` and put it in `assets/images/`. Commit it with the article.
4. **Add the image and visible credit.** Use a `<figure>` containing an `<img>` and a `<figcaption>`. The alt text describes what the image shows; the caption gives the source and the rights/credit notice. Link the source and the licence when the terms require it.
5. **For a social preview, check that the permission covers that use too.** Only then add an absolute `og:image` URL and `og:image:alt` to the article's `<head>`. A separate 1200×630 export usually works well. Do not add a preview image that is not actually hosted at that URL.

Example for a **licensed** image (replace every bracketed field with real, verified details):

```html
<figure class="article-figure">
  <img src="../../assets/images/descriptive-name.webp"
       width="1200" height="675" loading="lazy" decoding="async"
       alt="Describe the visible scene and what matters in this article">
  <figcaption>
    Image: <a href="ORIGINAL-SOURCE-URL">Title or original source</a>
    by Creator, used under <a href="LICENCE-URL">exact licence</a>.
    Cropped for layout.
  </figcaption>
</figure>
```

For a Creative Commons image, follow the [Creative Commons TASL guidance](https://creativecommons.org/reusing-cc-licensed-content/): **Title, Author, Source and Licence**, plus indicate edits. A generic “Image: Google” or “© DC” credit does not provide reuse permission.

For a game screenshot, a caption might say “Screenshot captured by Peter D’Souza from *Game Title*. Game imagery © [verified rights holder].” The **permission basis** belongs in the asset log; this caption does not itself grant permission. For comic covers, check DC's or the relevant publisher's written terms or seek permission, especially for homepage decoration or social preview crops.

India's [Copyright Act, section 52](https://copyright.gov.in/Copyright_Act_1957/chapter_xi.html) includes fair-dealing provisions for criticism or review, but whether a particular image use qualifies depends on context. Seek permission when the image is merely decorative or the terms are uncertain.

## Safest sources, in order

1. **An official press kit or media library with written reuse terms.** Save the page URL and a PDF or screenshot of the licence terms as they appeared when downloaded.
2. **Your own gameplay screenshot**, used to illustrate criticism, review, or reporting about that game. The underlying game art remains copyrighted; your capture does not make it public domain. Use only what the article needs and check the publisher's current content policy.
3. **A Creative Commons or public-domain image.** Verify the exact licence on the original host, comply with attribution and modification rules, and avoid licences that prohibit commercial use if the site may carry ads.
4. **Written permission from the copyright owner or their press agency.** Retain the email or licence agreement.

Do not treat Google Images, Pinterest, Reddit, a wiki, a fan account, a wallpaper site, a retailer listing, or another publication as a licence. They may help locate the original owner, but they do not normally grant reuse rights.

## Editorial-use test

Before relying on fair dealing or fair use, ask:

- Is the image directly discussed or genuinely necessary to illustrate the criticism, review, or reporting?
- Are you using only the number, size, and resolution reasonably needed for that purpose?
- Does the article add analysis rather than using the image as decoration or a substitute for official art?
- Have you credited the game, publisher/copyright owner, and source?
- Does the use avoid implying that the publisher sponsors or endorses Fourth Frame?
- Could the image contain separately licensed music, celebrity likenesses, sports branding, artwork, or other third-party material?

If an image is only there to make the homepage look attractive, obtain an express licence or use original commissioned/generated abstract art instead of relying on an editorial exception.

## Publisher notes

- **Halo / Microsoft:** Follow the Game Content Usage Rules linked from [Microsoft's copyright permissions page](https://www.microsoft.com/en-us/legal/intellectualproperty/copyright/permissions) before publication. Use the game title referentially and do not make Fourth Frame look official or Microsoft-endorsed.
- **Mass Effect / EA:** [EA's current content policy](https://help.ea.com/en/articles/security-and-rules/ea-content-policy/) permits certain fan sites and passive banner-ad monetisation subject to its conditions, but warns against implying affiliation, merging EA branding with your own, and using third-party licensed material. Follow its required disclaimer when displaying EA game content.
- **Batman / DC:** [DC's terms](https://www.dc.com/terms) protect images and other site content. A DC website image, comic cover, or promotional still should not be assumed to be a free press asset. Check an explicit media-use licence or obtain permission.
- Policies can change. Recheck the source page when adding an image, not just when this checklist was written.

## Asset log

| File | Article | Copyright owner | Original source URL | Permission/licence basis | Required credit | Date checked |
| --- | --- | --- | --- | --- | --- | --- |
| Example: `halo-combat.jpg` | Halo reboot | Microsoft | Official source URL | Xbox content policy / editorial commentary | © Microsoft / Xbox Game Studios | YYYY-MM-DD |
