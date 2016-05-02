from ascension import *

game = Ascension()

l = game.leagues[0]
p = l.players[0]

for league in game.leagues:
    league.process_episode_results()

game.print_leaderboard('essos','51')