---
title: "Master one way, or take what works from everywhere?"
slug: master-one-way-or-mix
type: "Journal"
description: "A development note on the central deck-building choice in Masters of the Way: a focused martial art or a flexible mixed deck."
summary: "The question behind the deck builder is also the question behind the whole game."
category: "Masters of the Way / Design"
tags: ["Masters of the Way", "Game development", "Card games", "Martial arts"]
related: ["what-made-elden-ring-great"]
cover_label: "DEVELOPMENT JOURNAL"
---

The first question in *Masters of the Way* isn't who you fight. It's how you want to fight. Do you devote a deck to one martial art, or borrow the best tools from several?

In the current [browser game](https://peterdsouza247.github.io/masters-of-the-way/), a deck that commits at least three quarters of its cards to one art earns a mastery passive and access to two master cards. A mixed deck gives that up, but draws a larger hand and can cover more ranges. The aim is a real choice, not a right answer hidden behind the numbers.

## The range argument

There are three places a fight can happen: Far, Close and Ground. Boxing wants the pocket. Taekwondo has reasons to stay out of it. Judo can turn a standing exchange into top position; Brazilian jiu-jitsu wants the floor. Those are game identities drawn from the arts, rather than a claim that an actual fight can be reduced to three zones.

The deck builder is where those identities collide. A focused deck gets stronger at doing its own thing. A mixed one has more ways to respond when the fight moves somewhere uncomfortable. Because cards are range-gated, the choice becomes visible every time a hand looks powerful but cannot yet be played.

## What still needs testing

The design target is for pure and mixed decks to remain competitive across matchups. A simulator helps reveal lopsided combinations, but players may find problems that a matchup matrix cannot: confusing grappling, a dead hand at the wrong range, or a mastery that feels better on paper than it does in a duel.

That is what I want the browser playtest to answer. A good mixed deck should feel resourceful; a single-art deck should feel like mastery, with meaningful weaknesses. If one choice simply wins more often, the argument at the heart of the game disappears.
