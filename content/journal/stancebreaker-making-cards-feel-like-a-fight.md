---
title: "Stancebreaker: making a hand of cards feel like a fight"
slug: stancebreaker-making-cards-feel-like-a-fight
type: "Journal"
description: "Stancebreaker's Android card hand, martial-arts presentation and next playtest, plus an exploratory vision for cinematic 3D fighting."
summary: "Readable cards and convincing exchanges have to work together on a phone."
category: "Stancebreaker / Cards and presentation"
tags: ["Stancebreaker", "Masters of the Way", "Game development", "Card games", "UI and UX"]
related: ["master-one-way-or-mix", "when-the-fight-stopped-moving", "from-browser-duel-to-full-game"]
cover_label: "STANCEBREAKER / DEVELOPMENT JOURNAL"
art: "mass"
published: 2026-11-20
---

*Masters of the Way* has become *Stancebreaker* for its Android edition. The central idea is still a martial-arts fight played through cards: judging distance, managing stamina and finding a sequence that puts the opponent where your next technique can work.

The phone version has a seven-opponent Tournament and a Deck Workshop for starter, custom and generated decks. There are seven fighters and 64 cards. That gives the player plenty to experiment with. The immediate problem is getting the cards and the fight to explain themselves on a small screen.

A martial-arts game can have a good rule for a throw and still leave the player wondering what just happened. It can also explain that rule perfectly in a card they cannot comfortably read. Both halves need attention.

## A hand you can actually browse

I wanted the hand fanned by default. It is a pleasing way to present cards, but it brings a fairly obvious problem: some of the information is covered by other cards.

The hand needs to scroll, and the card in focus needs to show its details clearly. It also needs to be obvious that more cards are available. Arrows, a scrollbar and a position counter help with that. They are small additions, but a player should not have to discover the rest of their hand by accident.

The selection pattern is now two taps. The first lifts a card into a potential selection; tapping the same card again plays it. Browsing the hand clears that selection. I like the idea that picking a card has a little physical hesitation to it, while keeping a separate confirmation dialogue out of every ordinary decision.

Cards that cannot be played are greyed out. Their rules remain available, and trying one produces a quiet explanation of the restriction. Range, stamina and position are already enough to think about. The interface should help explain the consequence of those rules.

The prototype's scrolling was janky. The latest work gives the cards stable dimensions and separates browsing from selection more carefully. Whether it feels comfortable under a thumb is still a phone-playtest question.

## Give the exchange time to register

I also asked for slower animation. A move can finish correctly and still pass too quickly for the player to connect it to the card they chose.

The pixel fighters, arenas and technique illustrations now have a shared visual direction. The card images represent technique families, while fighter portraits and style emblems help identify the character and art. Text still has to do its job; a more attractive card is not much use if its rule disappears into the decoration.

What I want to see in an exchange is the important change. A strike closes the distance or meets a guard. A clinch creates an opportunity for a throw. A ground position gives one fighter control and leaves the other looking for an escape. The animation and the displayed state need to agree about who achieved what.

That becomes especially important during the opponent's turn. A short combination should look connected enough that the player can follow it, while remaining clear about each action that resolved.

## The next test needs unfamiliar players

The new menus put learning, choosing a fight and building a deck into more distinct places. A new profile starts with gentler defaults, while the other difficulty and tournament rules remain available.

I want to know whether someone can finish the lessons and enter a fight without help. After that, I want to know which parts of the duel make sense. Can they explain why a technique was unavailable? Do they recognise a useful counter? When a throw puts them on the ground, do they understand the options they still have?

The Deck Workshop needs the same scrutiny. A legal deck is a starting point for experimentation. It does not guarantee that every matchup will be equally comfortable, especially when a fighter's plan depends on keeping the action standing.

The tester build keeps the full Tournament and deck tools available, with optional feedback that the player chooses to share. Automated checks already cover rules, saves and a range of interface flows. They do not establish whether a new player can read a crowded hand or whether a seven-fight run stays enjoyable on an actual phone.

## A cinematic 3D engine, eventually

The longer-term idea I would like to explore is a cinematic 3D fighting engine for *Stancebreaker*. I want connected strikes, blocks, counters, throws and submissions to convey the character of each martial art more convincingly.

There is a significant design choice to make before treating that as a production plan. A 3D presentation of the card game could retain its tactical decisions and choreograph the results. A game with direct fighting controls would need a different approach to input, timing and balance. I have not settled that choice, and better models would not settle it for me.

The first useful slice would be two fighters in one arena, with enough techniques to complete a bout. A throw should keep its contact points. A camera cut should make an exchange clearer. The result should remain understandable when the fighters grapple, separate or reach the floor.

That work would depend on funding, an appropriate animation pipeline and a prototype that earns the larger scope. It is a future vision, rather than a promised update or a feature being sold with the current game. I would like to release *Stancebreaker* at an accessible price; first, the cards in the player's hand need to make them want another fight.
