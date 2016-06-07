from ascension import *
import pdb

game = Ascension(55)
# print game.print_missing_votes_for_episode(ep=53)

# for ep in range(51,54):
	
	# game = Ascension(ep)
	# l = game.leagues[0]
	# p = l.players[0]

	# Process the latest votes / missions
	# for league in game.leagues:
		# Process Full Results
	    # league.process_episode_results(missions=True)

		# Process Voting Only
	    # league.process_episode_results(missions=False)

	    # Weekly Score Disctribution
	    # league.calculate_weekly_vote_distribution()

	# Inspect the episode_scores for a particular episode

	# print game.print_episode_scores('essos',str(ep)), '\n'
	# print game.print_episode_scores('westeros',str(ep)), '\n'
	# print game.print_episode_scores('dragon',str(ep))

# Recover after crash
# pdb.pm()

# Inspect who hasn't voted for the current episode
# game.print_missing_votes_for_episode(ep=52)


for league in game.leagues:
    league.process_episode_results(missions=True)