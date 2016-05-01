from ascension import *

game = Ascension()

for league in game.leagues:
    league.process_episode_results()

game.print_leaderboard('essos','51')