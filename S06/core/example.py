from ascension import *
import pdb

for ep in range(51,54):
	
	game = Ascension(ep)

	# l = game.leagues[0]
	# p = l.players[0]

	# Process the latest votes / missions
	for league in game.leagues:
	    league.process_episode_results(missions=True)

	# Inspect the episode_scores for a particular episode
	print game.print_episode_scores('essos',str(ep)), '\n'
	print game.print_episode_scores('westeros',str(ep)), '\n'
	print game.print_episode_scores('dragon',str(ep))

# Recover after crash
# pdb.pm()

# Inspect who hasn't voted for the current episode
# game.print_missing_votes_for_episode(ep=52)