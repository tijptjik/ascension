#!/usr/bin/env python

import simplejson
import pandas as pd
import operator
import pdb
from firebase import firebase
from tabulate import tabulate

from league import *

'''
GAME
'''

class Ascension(object):
    """Game Object for Ascension Crossed Banners"""
    def __init__(self, firebase_url = 'https://ascension.firebaseio.com'):
        super(Ascension, self).__init__()
        self.ref = firebase.FirebaseApplication(firebase_url, None)
        self.db = self.ref.get('/', None)
        
        self.awards = ['wit','damage','jockey','style','support']
        self.rank_score = {"1":20,"2": 8}
        self.diplomacy_performance_penalty = [0,0,0.25,0.5,0,0.25]
        self.violence_performance_penalty = [0,0.5,0.25,0,0.25,0.5]

        self.rosters = self.db['rosters']

        self.players = self.db['players']
        self.episode_scores = self.db['episode_scores']
        self.player_award_scores = self.db['player_award_scores']
        self.player_episode_scores = self.db['player_episode_scores']
        self.leaderboard = self.db['leaderboard']

        self.character_health = self.db['character_health']

        self.episodes = self.setup_episodes()
        self.characters = self.setup_characters()
        self.leagues = self.setup_leagues()

        self.most_recent_episode = filter(lambda x : x.current, self.episodes.values())[0]

    def setup_episodes(self):
        return {id: Episode(**e) for (id, e) in self.db['episodes'].iteritems()}

    def setup_characters(self):
        return {id: Character(**c) for (id, c) in self.db['characters'].iteritems()}

    def setup_leagues(self):
        # DEVELOPER MODE : ONLY SHOW ESSOS DATA
        # return [League(l, self) for l in self.db['leagues'].keys() if l == 'essos']
        return [League(l, self) for l in self.db['leagues'].keys()]


    def update_episode_scores(self, keys, scores):
        '''EPISODE SCORES PER CHARACTER PER AWARD

        'episode_scores'
            <league_id>+<episode_id>+<award> :
                "episode" : <episode_id>,
                "award" : <award>,
                "scores" : 
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>

        '''
        firebase_key = "{league}{episode}{award}".format(**keys)
        self.ref.put('/episode_scores/', firebase_key, scores)
        
        self.episode_scores.update({firebase_key : scores})


    def update_player_award_scores(self, keys, scores):
        ''' PLAYER SCORES PER CHARACTER PER AWARD

        'player_award_scores':
            <league_id>+<episode_id>+<award>+<player_id> :
                "episode" : <episode_id>,
                "award" : <award>,
                "player" : <player_id>,
                "scores" : 
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
                    <character_id> : <score>
        '''
        firebase_key = "{league}{episode}{award}{player}".format(**keys)
        self.ref.put('/player_award_scores/', firebase_key, scores)

        self.player_award_scores.update({firebase_key : scores})


    def update_player_episode_scores(self, keys, scores):
        '''PLAYER SCORES PER AWARD PER EPISODE

        'player_episode_scores':
            <league_id>+<episode_id>+<player_id> :
                "episode" : <episode_id>,
                "player" : <player_id>,
                "scores" : 
                    <award> : <score>
                    <award> : <score>
                    <award> : <score>
                    <award> : <score>
                    <award> : <score>
        '''
        firebase_key = "{league}{episode}{player}".format(**keys)
        self.ref.put('/player_episode_scores/', firebase_key, scores)

        self.player_episode_scores.update({firebase_key : scores})

    def update_leaderboard(self, keys, scores):
        ''' PLAYER SCORES PER EPISODE

        'leaderboard':
            <league_id><episode_id> :
                "episode" : <episode_id>,
                "scores" : 
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>

        '''
        firebase_key = "{league}{episode}".format(**keys)
        self.ref.put('/leaderboard/', firebase_key, scores)

        self.leaderboard.update({firebase_key : scores})

    def print_leaderboard(self, league, episode):
        key = league + episode
        player_names = [self.players[name]['first_name'] for name in self.leaderboard[key]['scores'].keys()]
        scores = self.leaderboard[key]['scores'].values()
        leaderboard = dict(zip(player_names, scores))

        scores = sorted(leaderboard.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Player','Score'],tablefmt="pipe",numalign="right")


'''
CHARACTERS
'''

class Character(object):
    """Game of Thrones Character"""
    def __init__(self, id, bio, name, house, prominence, diplomacy, violence):
        super(Character, self).__init__()
        self.id = id
        self.bio = bio
        self.name = name
        self.house = house
        self.prominence = prominence
        self.diplomacy = diplomacy
        self.violence = violence

    def __repr__(self):
        numeral = [0,'I','II','III','IV','V']
        return '<{} ({}) {}/{}>'.format(self.name, numeral[self.prominence], self.diplomacy, self.violence)


'''
EPISODES
'''

class Episode(object):
    """Game of Thrones Character"""
    def __init__(self, airdate, current, episode_number, has_aired, number, title):
        super(Episode, self).__init__()
        # TODO Set as datetime
        self.airdate = airdate
        self.current = current
        self.episode_number = episode_number
        self.has_aired = has_aired
        # TODO Automatically set episode as aired
        self.check_episode_aired()
        self.number = number
        self.title = title

    def __repr__(self):
        numeral = [0,'I','II','III','IV','V']
        return '<S06E{} ~ {}>'.format(self.episode_number, self.title)

    def check_episode_aired(self):
        pass

if __name__ == "__main__":
    game = Ascension()
    
    # for league in game.leagues:
        # league.process_episode_results()

    # DEVELOPER
    for league in game.leagues[0:1]:
        league.process_episode_results()