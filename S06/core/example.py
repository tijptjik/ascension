from ascension import *
import pdb

game = Ascension(52)

# l = game.leagues[0]
# p = l.players[0]

# Process the latest votes / missions
for league in game.leagues[1:]:
    league.process_episode_results(missions=True)

# Inspect the episode_scores for a particular episode
print game.print_episode_scores('essos','52'), '\n'
print game.print_episode_scores('westeros','52'), '\n'
print game.print_episode_scores('dragon','52')

# Recover after crash
# pdb.pm()

# Inspect who hasn't voted for the current episode
# game.print_missing_votes_for_episode(ep=52)