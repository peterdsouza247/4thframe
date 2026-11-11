---
title: "Last Lantern: Bosses That Change the Next Run"
slug: "last-lantern-bosses-boons-and-another-run"
type: "Journal"
description: "Distinct guardians, shuffled roads, difficult boon choices and local achievements: the next questions for Last Lantern's replayability."
summary: "A boss needs its own answer. Its reward should leave a decision behind."
category: "Last Lantern / Encounters and progression"
tags: ["Last Lantern", "Game development", "Boss design", "Roguelites", "Progression"]
related: ["last-lantern-fewer-buttons-better-decisions", "last-lantern-making-the-dark-worth-exploring", "when-the-fight-stopped-moving"]
cover_label: "LAST LANTERN / JOURNAL 03"
art: "elden"
---

One of the ideas I wanted to take from *Teamfight Tactics* was the way a unit can change a fight through its behaviour. Calling reinforcements, protecting another target or creating a dangerous area can alter what everyone else needs to do.

For *Last Lantern*, that suggested a useful test for the guardians: if I removed their names and changed their sprites, would the player still recognise which encounter they were in?

Larger health bars would not answer that. The bosses needed different demands on the Rogue's movement, and rewards that helped make the next road feel different too.

## Give each guardian a problem to solve

The 0.12 design separates encounters that require breaking protective wards from those that reward moving behind the guardian during a recovery window. Reinforcements arrive during attacks, with limits on how many can remain alive and how many can be summoned in a phase.[^1]

Candle-Eye asks the Rogue to deal with watch-eyes while leaving marked ground. The Root Matron has root hearts to sever. The Bell-Ram asks the player to move inside a ring and use the silence that follows. The Rimehorn's charge creates a different movement problem and an opportunity once it is exhausted.

Those are the intended distinctions. They will only feel distinct if the warning, danger and opening are readable in an ordinary fight. The player should be able to learn why moving helped without consulting a page of internal rules.

Summons also need a purpose beyond making the screen busier. A ranged enemy changes the safety of an approach. A nuisance near the lantern can make an opening at the boss more expensive to pursue. The cap matters because a fight should remain recoverable after a mistake; an unlimited crowd would eventually bury the guardian's own behaviour.

## Shuffle the journey, keep the destination

The first nine regions now shuffle together for a new expedition. Nox remains the tenth encounter. Region identity determines the mechanics and the boon pair; position in the run determines the health and reward scaling.[^1]

That should make an early guardian more consequential. Meeting Candle-Eye first gives a different opening set of demands from meeting the Thorn Marshal. The equipment and skills available at that point also change what the player can comfortably attempt.

It is not the same as generating a completely new world. These remain authored regions and encounters in a different order. Their value has to come from how they interact with the company's changing resources, rather than the shuffle alone.

## The reward should require a judgement

Each of the first nine defeated guardians offers two themed boons. The player takes one for that expedition, accepting its penalty alongside its benefit. Nox ends the journey, so there is no final gameplay boon with nowhere left to use it.[^1]

The Watching Orchard pair makes the intention fairly clear: a larger protective light at the cost of some Tank damage, or faster searching at the cost of Rogue health. One changes the company's safety; the other makes trips into danger quicker while reducing the margin for error.

These choices should depend on the run. Faster searching may be attractive when detours are paying off. More light may be useful when returning to the company has become difficult. If one option wins regardless of the party and equipment, its alternative is occupying space rather than providing a decision.

## Remember the run without requiring more grind

The Chronicle now includes a named local profile, twelve achievements and links to the runs that earned them. The medals provide no combat stat bonuses.[^2]

I wanted a reason to remember an expedition beyond its score. I also wanted every new attempt to remain a reasonable place to learn. Tying basic combat strength to permanent achievement rewards would make failure harder to interpret: did the player need a better decision, or simply more completed runs?

Profiles and achievements are local, rather than a verified online competitive system. Their role is to record a history worth looking back through. Different parties, equipment and guardian orders still have to provide the reason to play again.

## Then the game froze after Candle-Eye

After defeating Candle-Eye as the first boss, I hit a freeze. That is the less glamorous part of adding a new progression loop: the reward and transition have to work before anyone can judge whether the next choice is enjoyable.

The report makes the next verification quite concrete. Finish that encounter on a phone, reach camp, resolve the boon and leave for the next road. Continue from a save around the same transition and check the sequence again. Until that sequence has been verified on the device, I cannot call the progression loop finished.

Automated encounter checks are useful, but a successful simulated journey is not evidence that every player can complete the same sequence through the interface. Once the transition is dependable, the more interesting question becomes available again: did this boss make the player reconsider how to handle the next road?

[^1]: [The 0.12 guardian and boon guide](https://github.com/peterdsouza247/last-lantern/blob/38e941000f1e591e4bbeddbc8c5d471ae1449179/docs/GUARDIAN_ROADS.md), documenting the intended mechanics, reinforcement caps and trade-offs. Their presence in the build is separate from a claim of finished human balance.

[^2]: [The 0.12 release notes](https://github.com/peterdsouza247/last-lantern/blob/38e941000f1e591e4bbeddbc8c5d471ae1449179/docs/RELEASE_0.12.0.md). This entry records the design change and the subsequent play report; it is not a hotfix announcement.
