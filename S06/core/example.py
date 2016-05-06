from ascension import *
import pdb

game = Ascension()

# l = game.leagues[0]
# p = l.players[0]

# Process the latest votes / missions
for league in game.leagues:
    league.process_episode_results()

# Inspect the leaderboard for a particular episode
print game.print_leaderboard('essos','51')

# Recover after crash
# pdb.pm()