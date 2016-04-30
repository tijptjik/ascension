#!/usr/bin/env python

import simplejson
import pandas as pd
import operator
from firebase import firebase
from abc import ABCMeta, abstractmethod
from collections import Counter
from tabulate import tabulate

class Ascension(object):
    """Game Object for Ascension Crossed Banners"""
    def __init__(self, firebase_url = 'https://ascension.firebaseio.com'):
        super(Ascension, self).__init__()
        self.ref = firebase.FirebaseApplication(firebase_url, None)
        self.db = self.ref.get('/', None)
        
        self.awards = ['wit','damage','jockey','style','support']
        self.rank_score = {"1":20,"2": 8}

        self.leagues = self.setup_leagues()
        self.characters = self.setup_characters()
        self.episodes = self.setup_episodes()
        self.episode_scores = self.db['episode_scores']

    def setup_leagues(self):
        return [League(l, self) for l in self.db['leagues'].keys()]

    def setup_characters(self):
        return {id: Character(**c) for (id, c) in self.db['characters'].iteritems()}

    def setup_episodes(self):
        return {id: Episode(**e) for (id, e) in self.db['episodes'].iteritems()}


class League(object):
    """League in Ascension Crossed Banners"""

    def __repr__(self):
        return '<{0} League>'.format(self.name.title())

    def player_filter(self, player):
        return 'games' in player and type(player['games']) is not bool and self.name in player['games']

    def vote_filter(self, vote):
        return vote['league'] == self.name

    def mission_filter(self, mission):
        return mission['league'] == self.name

    def __init__(self, name, game):
        super(League, self).__init__()
        self.name = name
        self.game = game

        for k, v in game.db['players'].iteritems():
            v['id'] = k

        self.players = filter(self.player_filter, game.db['players'].values())
        
        self.votes = filter(self.vote_filter, game.db['votes'].values())
        self.missions = filter(self.mission_filter, game.db['missions'].values())
        
        self.players = self.init_players()

    def init_players(self):
        for player in self.players:
            player['league'] = self
            player['house'] = player['house'][self.name]
            player['roster'] = player['games'][self.name]
            del player['games']
        return [Player(**player) for player in self.players]

    def score_weekly_episode(self):
        current_episode = filter(lambda x : x.current, self.game.episodes.values())[0]
        episode_votes = filter(lambda v: v['episode'] == str(current_episode.number), self.votes)
        
        
        for award in self.game.awards:

            score = ScoreCounter()

            for vote in episode_votes:
                for rank, points in self.game.rank_score.iteritems():
                    character = vote['vote_' + award + "_" + rank]
                    score.update({character:points})

            firebase_key = "{}{}{}".format(self.name, current_episode.number, award)
            self.game.episode_scores.update({firebase_key : score})

            # print '\n## {}\n'.format(firebase_key.upper())
            # print score
    

    def run_weekly_diplomatic_missions(self):
        raise NotImplementedError

    def award_vote_keys(self):
        return ["vote_"+ award + "_" + str(y) for award in self.game.awards for y in [1,2]]


class House:
    __metaclass__ = ABCMeta

    def __init__(self, wit=0, damage=0, jockey=0, style=0, support=0):
        self.wit = wit
        self.damage = damage
        self.jockey = jockey
        self.style = style
        self.support = support
    
    def __str__(self):
        return 'House {0}'.format(self.name.title())

    @abstractmethod
    def run_diplomatic_mission(self):
        pass

    @abstractmethod
    def run_assassination_mission(self):
        pass


class HouseArryn(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'jockey':20}
        super(HouseArryn, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass
        

class HouseBolton(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'damage':10,'support':10}
        super(HouseBolton, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseGreyjoy(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'damage':20}
        super(HouseGreyjoy, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseIndependent(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {style:'10','support':10}
        super(HouseIndependent, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseLannister(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'wit':10,'jockey':10}
        super(HouseLannister, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseMartell(House):
    def __init__(self, name):
        self.name = name
        self.bonus = dict(wit=5, damage=5, jockey=5, style=5, support=5)
        super(HouseMartell, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseMeereen(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'wit':20}
        super(HouseMeereen, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseMinor(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'wit'10,'support':10}
        super(HouseMinor, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseNightswatch(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'damage':10,'support':10}
        super(HouseNightswatch, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseStark(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'support':20}
        super(HouseStark, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseTargaryen(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'damage':10,'jockey':10}
        super(HouseTargaryen, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseTyrell(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'style':20}
        super(HouseTyrell, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


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


'''
LEAGUES
'''

'''
PLAYERS
'''

class Player(object):
    """A League Player"""
    def __init__(self, league, id, alias, alias_short, email, facebook, first_name, full_name,
                    roster=None, house=None, missions=None, votes=None):
        super(Player, self).__init__()
        self.id = id
        self.league = league
        self.alias = alias
        self.alias_short = alias_short
        self.email = email
        self.facebook = facebook
        self.first_name = first_name
        self.full_name = full_name
        self.roster = roster
        self.house = self.ofHouse(house)
        self.missions = self.collect_missions()
        self.votes = self.collect_votes()

    def __repr__(self):
        return '<{} @ {}>'.format(self.first_name, self.house.name.upper())

    def ofHouse(self, house):
        house_map = {
            "arryn" : HouseArryn,
            "bolton" : HouseBolton,
            "greyjoy" : HouseGreyjoy,
            "independent" : HouseIndependent,
            "lannister" : HouseLannister,
            "martell" : HouseMartell,
            "meereen" : HouseMeereen,
            "minor"   : HouseMinor,
            "nightswatch" : HouseNightswatch,
            "stark" : HouseStark,
            "targaryen" : HouseTargaryen,
            "tyrell" : HouseTyrell,
        }

        return house_map[house](house)

    def collect_votes(self):
        return filter(lambda v: v['player'] == self.id, self.league.votes)

    def collect_missions(self):
        return filter(lambda m: m['player'] == self.id, self.league.missions)



'''
ROSTERS
'''

'''
VOTES
'''


if __name__ == "__main__":
    game = Ascension()
    # for league in game.leagues:
        # print league.players
    for id, epiosode in game.episodes.iteritems():
        print epiosode
    # for id, character in game.characters.iteritems():
        # print character

'''
UTILS
'''

class ScoreCounter(Counter):
    def __str__(self):
        # return "\n".join('{} {}'.format(k, v) for k, v in
            # sorted(self.items(), key=operator.itemgetter(1), reverse=True))
        scores = sorted(self.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Character','Score'],tablefmt="pipe",numalign="right")