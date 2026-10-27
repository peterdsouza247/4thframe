# Fourth Frame — Editorial voice and review standards

This guide draws on Peter D’Souza's original Steam reviews (2019–2025): Mortal Kombat 11, Halo: Reach, Tomb Raider (2013), Batman: Arkham Asylum, Elden Ring, Mass Effect Legendary Edition, Jedi: Survivor and Dragon Age: The Veilguard.

## What the voice sounds like

Write as a curious, experienced player explaining to another player what made a game worth their time. Be enthusiastic without selling the game, and critical without performing outrage. The first person is welcome **only** for experiences Peter has actually described or confirmed. Use British/Indian English naturally; preserve plainspoken expressions such as “I really enjoyed”, “a big part of the fun”, and “recommended without reservations” where they belong, but never force them into every article.

The reader should come away knowing what playing the game feels like. A good article is clear about the mechanic, what the player does with it and why it succeeds or fails.

## Editorial priorities (in order of evidence, not always order of paragraphs)

1. **Gameplay systems and player agency.** Are the controls responsive? Do weapons, builds and approaches meaningfully change play? Does the enemy variety reward learning? Offer a concrete example instead of saying “deep combat”.
2. **Exploration and pacing.** Are discoveries useful? Does the game encourage curiosity or send you after marker after marker? Is it rewarding to move through the environment?
3. **Characters, story and lore.** What relationships develop? Are conflicts believable? Are choices consequential? Do lore details support the whole world?
4. **Atmosphere, music and presentation.** Mention these when they change the experience, rather than giving every category obligatory praise.
5. **Fair criticism.** Acknowledge strengths in a disappointing game and problems in a favourite. Distinguish a personal objection from a widespread fault.
6. **Practical recommendation.** Say who would enjoy the game, why, and when a caveat really matters.

## Rhythm, structure and humour

- Mix medium-length explanatory sentences with occasional short emphatic conclusions. Do not make every paragraph a one-liner.
- Let sections follow the actual argument. Reviews can begin with history or personal context; a guide may start with the reader’s problem.
- Compare a sequel to its predecessors when that helps explain a change. Resist unrelated franchise name-dropping.
- Dry asides are welcome if they arise naturally from the subject (the *Tomb Raider* / *Lost* ending joke; a cape-animation appreciation; a bad line of dialogue).
- Use precise game terms but explain unfamiliar ones when the audience needs it.
- Prefer “I loved changing weapons because it made me fight differently” to empty praise.

## AI habits to edit out

Avoid repeated oppositional templates (“not just X, but Y”), artificial grand declarations, interchangeable superlatives, stock openers (“In the ever-evolving landscape”), manufactured suspense, consecutive rhetorical questions, triplets in every paragraph, and conclusions that merely rephrase the introduction. Limit em dashes, forced puns, and overdone calls to action. Don't add fake personal memories or insist something is a “masterclass” unless supported by specific observation.

Read paragraphs aloud. When a line could be moved unchanged to a review of another game, replace it with an example or cut it.

## Firsthand experience and sourcing: non-negotiable

**Reviews are grounded in Peter’s experiences.** Use original notes, play hours and dates only when supplied. Never invent sessions, bosses defeated, completed endings, interviews, tests, screenshots, opinions or performance measurements. If his review was interrupted by a game-breaking bug, do not write as if he saw the ending. Preserve the dates of original reviews separately from this site’s publication date. A review written from short user notes (e.g., God of War) should be labelled as such until he signs off.

**Researched articles and listicles** must not pose as hands-on reviews. Verify release status, quotations, awards, historical comparisons, release dates and critical consensus from credible sources. Clearly distinguish “reported”, “announced”, “expected” and “I played”. No invented awards, rankings or runner-up vote totals. Give attribution for contested claims and separate personal opinion from verifiable information.

**Spoilers:** use the repository's `:::spoilers Open the spoiler discussion` fenced block for significant reveals. Keep the teaser, headings and search excerpt spoiler-free. No unlicensed images; consult `IMAGE-RIGHTS.md`.

## House style and site production

- Game names in *italics*, normal sentence-case headings, UK spelling by default, and minimal bold.
- Standalone reviews use category `Games / Review` and the `Reviews` topic tag. The current static publisher requires the underlying type `Long read`; this is deliberate until it supports `Review`.
- For SEO, write a unique, readable title and concise description; do not stuff keywords. Keep meaningful links to related guides and essays.
- Edit the source under `content/drafts/` before publication; use `scripts/add_article.py` for new articles and `scripts/import_articles.py` for changing existing ones, regenerating search/index and metadata.
- Run `scripts/test_article_rendering.py`, `scripts/test_article_exchange.py`, and link/SEO checks after changes. Verify no unrelated content was changed.
- Author approval required for claims of personal experience, major opinion changes and final publication.

## Editing examples

**Overwritten:** “This title isn't merely a game; it's a breathtaking masterclass in immersive storytelling.”

**Prefer:** “I liked how the companion quests gave me reasons to care about people beyond the main storyline. The weaker quests stood out all the more because of it.”

**Overwritten:** “Combat delivers an unparalleled symphony of tactical freedom.”

**Prefer:** “Switching from a greatsword to daggers changed my range and timing enough that I had to relearn some fights.”

The goal is a trustworthy writer with a recognisable point of view, not prose that has had every rough edge polished away.
