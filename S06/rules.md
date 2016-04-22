# Ascension II : Crossed Banners

The fog of war descends on Westeros...

## Game Summary

Ascension is played alongside season 6 of HBO's Game of Thrones. You play online by selecting your favourite characters, and having them compete in award categories of _wit_, _damage_, _jockey_, _style_ and _support_. Points are awarded by fellow players whom cast votes each episode.

It is similar to fantasy football, as you build up a roster of characters at the start of the season, and get points for their performance in each episode.

In keeping with the Game of Thrones logic, you can send your characters on diplomatic and assassination missions; gathering intelligence or taking out characters from other player's rosters. But be careful! Failed attempts leave you exposed! Plot at your own peril...

## Quick Start

1. **Sign Up**. Sign up at [ascension.type.hk](http://ascension.type.hk).
2. **Pick a House**. Houses boost the characters you pick from that house, have special abilities, and are public knowledge.
3. **Pick 7 Characters for your Roster**. Every episode your characters will compete for points in the award categories (wit, damage, jockey, style and support). Players all vote for the characters who are most deserving of points in each category, so pick your characters wisely. Rosters are secret. [Follow a strategy](#Picking-Your-Characters).
4. **Watch the Weekly Episode**. Watch the episode within a week of it being aired.
5. **Cast your Weekly Votes**. For each of the award categories, vote who most deserves the award that week. Votes are public.
6. **Initiate Weekly Missions**. Send one of your characters to gather intel, and/or assasinate characters from another roster. Missions are secret.
7. **Consult the Chronicles**. A chronicle is sent out to all players with the voting record, and the results from the spy and murder missions, some private, some public.
8. **Rank on the Leaderboard**. Leaderboard is updated with the weekly character points.

## Rules

The game is played in a league of 12 players. Each player represents a **[House](#Houses)** and fields a **[Roster](#Roster)** of 7 GoT Characters. **[Characters](#Characters)** are used to score points across 5 **[Award Categories](#Award-Categories)**. Points are awarded based on **[Popular Vote](#Popular-Vote)** after each episode. The player with the most points at the end of the season, ascends to the throne.

### Award Categories

* **Wit** - smartest or most piercing delivery of a line.
* **Damage** - physical and mental destruction, dealt or received.
* **Jockey** - most promising manoeuvring for the Iron Throne. 
* **Style** - best look, appearance or use of props.  
* **Support** - most helpful supporting character.

### Roster

The characters needn't belong to the roster's house.

### Affilition

All 12 available affiliations have [abilities & score multipliers](https://github.com/tijptjik/ascension/blob/gh-pages/S06/houses.csv).

#### Available Houses 

* House Bolton
* Council of Meereen
* House Arryn
* House Greyjoy
* House Martell
* Independents
* Night's Watch & Free Folk
* League of Minor Orders
* House Targaryen & Dothraki Horde
* House Tyrell
* House Lannister
* House Stark

Of special note are the **Council of Meereen**, which consist of the formidable characters who remained to rule Meereen at the close of season 5; **House Arryn**, which might as well be House Baelish; **Independents** which gather the many mystics, magicians and maniacs of both continents; **Night's Watch & Free Folk** which have formed an unholy alliance; **League of Minor Orders** which gather nobility and clergy from the Order of the Sparrows, Slave traders from Essos, Lords of the House Frey and Ser Davos Seaworth; **House Tyrell** which includes their sworn bannerman from House Tarly; and **House Targaryen & Dothraki Horde** which contain many of the yet-to-be-introduced characters.

### Characters

1. Their `affiliation` to a given house;
2. Scoring potential, or `prominence`, 
3. Damage potential, or `violence`, and
4. Ability to gather intelligence, or `diplomacy`.

Each character has four main traits:

* **Affiliation**, either a house, a lesser house, or an independent.
* **Prominence**, how central is this character to Game of Thrones
* **Violence**, how deadly is this characer
* **Diplomacy**, how good is this character at winning information

#### Available Characters

All 88 available characters have an [affiliation & powers](https://github.com/tijptjik/ascension/blob/gh-pages/S06/character.powers.csv) and have a [bios](https://github.com/tijptjik/ascension/blob/gh-pages/S06/character.bio.csv) to remind you who they are.

#### Prominence


#### Fatality

* Probability of success
* Wounded is the reduction in scoring capacity
* Anonimity of Mission 
* The Underdog = if the total prominence of your deck is lower than the prominence of the target's deck, become lethal
* Unholy Alliance = a mechanism involving coordinated attacks 

The 5 Tiers 

| tier | % of success | wounded % | % of anonimity |
|------|---------|-------|

1.
2.
3.
4.
5. No performance pentalty
6. 
#### Diplomacy

1.
2.
3.
4.
5. No performance pentalty

* Probability of success
* Number of facts retrieved
* Class of facts retrieved
* Defence against attack
* Anonimity of Mission 


The 5 Tiers 

| Tier| Ability | Notes |
|-----|---------|-------|
  V   |
 I V  |
I I I |
 I I  |
  I   |


### Missions

Each week, characters can be sent on missions. One can be sent on a diplomatic mission, another on an assassination attempy.

Sending a character on a mission, makes them 75% as efficient at scoring points.

### Popular Vote

Players can log in to the Ascension game with the Facebook account they signed up with. They may then vote for both the winner and the runner-up (i.e. top 2) in each [Award Category](#Award-Categories). Scoring is done each Saturday at 12:00 Hong Kong time. Votes and Missions which have not been cast will not be considered.

#### Scoring and Awarding Points

A winning vote counts for 20 points, a runner-up vote scores 8 points. Characters racks up points in each award category, but before they are awarded to the players who fielded them, the points are first modified by the character's health (lower health is a negative multiplier) and a player's character and award category bonuses (bonuses are positive multipliers). In sum, **Characters** _score_ points based on _votes_, **Players** are _awarded_ points based on their character's _score_, _health_ and _bonus multipliers_. A player's points across their characters are summed up which becomes their episode score. The sum of the episode scores after 10 episodes is the season score, which determines the winner.

#### Voting for your own Characters

While it is possible to vote for characters on your own roster - smart move! you're basically awarding yourself points. Though, as votes are public record, it might send a strong signal your roster fielded this character, attracting unwanted, even murderous attention. The only exception to this rule are characters whom due to House Abilities are immune from attack. Your votes for these character will award you no additional points.


## Strategy

### Picking Your Characters

* Don't get killed.
* Play to your House's advantages.