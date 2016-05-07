from ascension import *
import pdb

game = Ascension(51)

# l = game.leagues[0]
# p = l.players[0]

# Process the latest votes / missions
for league in game.leagues:
    league.process_episode_results()

# Inspect the episode_scores for a particular episode
print game.print_episode_scores('essos','51')

# Recover after crash
# pdb.pm()