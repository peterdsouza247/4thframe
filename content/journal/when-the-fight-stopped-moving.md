---
title: "When the fight stopped moving"
slug: when-the-fight-stopped-moving
type: "Journal"
description: "How a range stalemate exposed a flaw in Masters of the Way, and what the current fix still needs from live playtests."
summary: "A fight that neither side could advance taught me more than a clean knockout."
category: "Masters of the Way / Playtesting"
tags: ["Masters of the Way", "Game development", "Playtesting", "Game design"]
related: ["master-one-way-or-mix"]
cover_label: "DEVELOPMENT JOURNAL"
---

One of the first useful reports about [Masters of the Way](https://peterdsouza247.github.io/masters-of-the-way/) described a duel that just kept going. Kevin and Shanna found a fight where both sides were stuck at Far range with hands full of cards they couldn't use. The turn counter advanced; the fight did not.

It was more than an AI mistake. Range is meant to be a tactical constraint, but the game needs a way to resolve a position where neither fighter can act. Otherwise a deck-building decision becomes an endless loop.

## The current response

The build now offers **Reset stance** when a player has no playable card: spend one stamina, discard the hand and draw again. The AI can do the same. If several turns still pass without action, the referee brings the fighters to Close range. A second stalemate there goes to a decision, and a hard turn cap is the final backstop.

The forfeit option also gives a player a deliberate way out of a match. It asks for confirmation and records the result rather than silently abandoning the duel.

## What code cannot confirm

Those paths exist in the game, but the reported Reyes-at-Far case still needs a live replay. I want a playtester to see the fix in a normal match and tell me whether it feels like a fair referee intervention or an invisible correction to a deck problem.

The lesson for the itch playtest is straightforward: a match ending is necessary, but *how* it ends matters. I would rather hear about an awkward decision than have a stuck fight quietly disappear from the record.
