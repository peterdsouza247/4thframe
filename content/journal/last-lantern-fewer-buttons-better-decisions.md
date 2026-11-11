---
title: "Last Lantern: Fewer Buttons, Better Decisions?"
slug: "last-lantern-fewer-buttons-better-decisions"
type: "Journal"
description: "Moving Last Lantern towards automatic combat, removing the forge and making equipment and skill choices easier to find at camp."
summary: "The abilities could happen automatically. The decisions still needed somewhere useful to live."
category: "Last Lantern / Controls and camp"
tags: ["Last Lantern", "Game development", "Game design", "UI and UX", "Automatic combat"]
related: ["last-lantern-making-the-dark-worth-exploring", "master-one-way-or-mix"]
cover_label: "LAST LANTERN / JOURNAL 02"
art: "elden"
---

I was not sure which items I could equip. The equippable ones were listed below the information I was already reading. In the skill screen, I also missed the second branch because it appeared after all the choices in the first.

Both are fairly small interface mistakes with substantial consequences. A choice may exist in the game, but if the player does not realise it is there, it contributes very little.

This became part of a wider question about *Last Lantern*: which decisions need my attention while the Rogue is moving, and which belong at camp?

## Let the company handle its abilities

The current direction is for attacks and special powers to happen automatically. On the road, the player concentrates on movement, returning towards the lantern and choosing a route. Equipment and skill decisions belong between roads.[^1]

I like the way an auto battler can let a prepared group express the decisions made before the fight. For *Last Lantern*, that still leaves the Rogue's position under direct control. Leaving a marked area, reaching a vulnerable target and deciding when to return to the company remain actions the player has to judge.

That makes encounter design more demanding. If every enemy can be beaten by standing nearby while the abilities fire, automatic combat has removed much of the game. The enemies need to create situations in which moving somewhere else is useful.

It also makes feedback more important. An automatic power has to be visible enough that the player can connect its effect to a character or item. Otherwise the camp choice may be meaningful in the simulation and almost invisible during play.

## Why remove the forge?

Earlier builds let unwanted equipment become scraps for a camp forge. It gave weaker finds a use and offered a more directed way to obtain gear. Those are sensible functions, but they also added another process to every camp.

I decided to remove forging and salvage. The 0.12 camp no longer asks the player to manage those materials or work through a separate crafting choice.[^2]

The cost is worth acknowledging. There is less direct control over generating a replacement for a weak slot. Better loot distribution now has to carry more of that responsibility. Removing a system does not remove the problem it was intended to solve.

What I want to gain is a clearer pause between roads: look at the finds, decide what to equip, choose skills and consider the guardian's boon. Those decisions already have enough to say about the next stage of the expedition.

## Put the options before their explanations

The equipment screen now puts available gear and the Equip action before the detailed comparison. The skill screen presents both branches before their upgrade nodes.[^2]

That ordering follows the problem I actually encountered. First I need to know what is available. Then I can compare it. A long explanation of one branch is useful after I know there is another branch beside it.

The same principle applies to a Legendary item. Its special effect needs a clear explanation, but the basic decision should be easy to find: who can use it, what it replaces and where to equip it. Colour and animated rarity effects can help recognition; they cannot do the work of arranging the information.

## What I want the next playtest to establish

Fewer buttons will not automatically produce better decisions. I want the field to demand attention to position and the camp to reward attention to the company. Either half can fail.

A useful playtest would show where someone hesitates: whether they can identify an upgrade, whether both skill paths are visible, and whether they understand why a choice changed the next fight. It should also reveal whether camp has become a pleasant break or still feels like work before the game resumes.

The existing checks can verify that equipping changes the intended values and that leaving camp preserves a choice. The more important interface test is whether someone can make that choice without needing me to explain where it is.

[^1]: [The 0.11 road-and-camp changes](https://github.com/peterdsouza247/last-lantern/blob/38e941000f1e591e4bbeddbc8c5d471ae1449179/docs/RELEASE_0.11.0.md).

[^2]: [The 0.12 forge removal and camp layout changes](https://github.com/peterdsouza247/last-lantern/blob/38e941000f1e591e4bbeddbc8c5d471ae1449179/docs/RELEASE_0.12.0.md). These are development notes on the 0.11–0.12 design changes, not a claim that phone usability has received final acceptance.
