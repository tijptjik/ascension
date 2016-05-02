#!/usr/bin/env python

import simplejson
import pandas as pd
import operator
import pdb
from firebase import firebase
from abc import ABCMeta, abstractmethod
from collections import Counter
from tabulate import tabulate

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
LEAGUES
'''

class League(object):
    """League in Ascension Crossed Banners"""

    def __init__(self, name, game):
        super(League, self).__init__()
        self.name = name
        self.game = game

        for k, v in game.db['players'].iteritems():
            v['id'] = k

        self.players = filter(self.filter_player, game.db['players'].values())
        
        self.votes = filter(self.filter_league, game.db['votes'].values())
        self.missions = filter(self.filter_league, game.db['missions'].values())
        self.intelligence = filter(self.filter_league, game.db['player_intelligence'].values())
        
        self.players = self.init_players()
        self.roster_ids = self.collect_player_rosters_ids()
        self.rosters = self.collect_player_rosters()

        self.character_health = self.collect_character_health()

        self.assign_rosters_to_players()

        self.current_episode = "00"
        self.current_episode_score = {}
    

    # Helper Methods

    def __repr__(self):
        return '<{0} League>'.format(self.name.title())

    def filter_player(self, player):
        return 'games' in player and type(player['games']) is not bool and self.name in player['games']

    def filter_league(self, obj):
        return obj['league'] == self.name

    def init_players(self):
        for player in self.players:
            player['league'] = self
            player['house'] = player['house'][self.name]
            player['roster_id'] = player['games'][self.name]

            del player['games']

        return [Player(**player) for player in self.players]


    def collect_player_rosters_ids(self):
        return map(lambda x: x.roster_id, self.players)

    def collect_player_rosters(self):
        return {roster_id: roster for roster_id, roster in self.game.rosters.iteritems() if roster_id in self.roster_ids}

    def collect_character_health(self):
        # Defaults
        for key, roster in self.rosters.iteritems():
            if key not in self.game.character_health:
                self.game.character_health[key] = dict(zip(roster.values(), [100]*7 ))

        return {key: roster for key, roster in self.game.character_health.iteritems() if key in self.roster_ids}

    def assign_rosters_to_players(self):
        for player in self.players:
            player.roster = self.rosters[player.roster_id]
            player.character_health = self.character_health[player.roster_id]
            player.roster_prominence = player.get_roster_prominence(self.game.characters)

    # Weekly Processes

    def process_episode_results(self, episode=None):
        if episode is None:
            episode = self.game.most_recent_episode
        
        self.score_weekly_episode(episode)
        # DEVELOPER
        self.run_weekly_diplomatic_missions(episode)        
        # DEVELOPER
        # self.run_weekly_assassion_missions(episode)
        # DEVELOPER
        # self.award_weekly_points(episode)

    def score_weekly_episode(self, episode):
        episode_votes = filter(lambda v: v['episode'] == str(episode.number), self.votes)
        
        for award in self.game.awards:

            score = ScoreCounter()

            for vote in episode_votes:
                for rank, points in self.game.rank_score.iteritems():
                    character = vote['vote_' + award + "_" + rank]
                    score.update({character:points})

            
            self.name, episode.number, award
            
            keys = {
                "league" : self.name,
                "episode" : episode.number,
                "award" :  award
            }

            self.current_episode = episode
            self.current_episode_score[award] = score

            self.game.update_episode_scores(keys, dict(score))


    def run_weekly_diplomatic_missions(self, episode):
        episode_missions = filter(lambda v: v['episode'] == str(episode.number), self.missions)

        for mission in episode_missions:
            print mission

        pass

    def run_weekly_assassion_missions(self, episode):
        episode_missions = filter(lambda v: v['episode'] == str(episode.number), self.missions)

        # Award points for succesful assassinations
        # Points are split between the number of assailants.
        # If a stronger assassin targets the same characters, 

        # INDEPENDENT : The faceless man the ability to take on other personas. If Jaqen kills a Character, they join this House's Roster

        # TARGARYAN : All Characters on this House's Roster gain $5\%$ Bonus on a succesful attack by a Dothraki Character

        # Update the personal Chronicle with the character damange they incurred.

        # Update the public chronicle about the deaths / damage
        pass

    def award_weekly_points(self, episode):
        
        leaderboard_scores = {}

        for player in self.players:

            player_episode_scores = {}

            for award in self.game.awards:
                
                award_score = self.current_episode_score[award]
                awarded_points = player.house.award_points(self, episode, award,
                    award_score, self.game.characters, player.character_health, player.missions)
                
                keys = {
                    "league" : self.name,
                    "episode" : episode.number,
                    "award" : award,
                    "player" : player.id
                }
                
                scores = {
                        'episode' : keys['episode'],
                        'player' : keys['player'],
                        'award' : keys['award'],
                        'scores' : dict(awarded_points)
                }

                player_episode_scores[keys['award']] = sum(dict(awarded_points).values())

                # print player, award, '\n\n', awarded_points

                # DEVELOPER
                self.game.update_player_award_scores(keys, scores)

            scores = {
                'episode' : keys['episode'],
                'player' : keys['player'],
                "scores" : player_episode_scores
            }

            leaderboard_scores[keys['player']] =  sum(player_episode_scores.values())

            # DEVELOPER
            self.game.update_player_episode_scores(keys, scores)

        scores = {
            'episode' : keys['episode'],
            "scores" : leaderboard_scores
        }

        # DEVELOPER
        self.game.update_leaderboard(keys, scores)

'''
HOUSES
'''

class House:
    __metaclass__ = ABCMeta

    def __init__(self, wit=0, damage=0, jockey=0, style=0, support=0):
        self.wit = wit
        self.damage = damage
        self.jockey = jockey
        self.style = style
        self.support = support
        self.immunity = None

        self.intelligence_logs = None
    
    def __str__(self):
        return 'House {0}'.format(self.name.title())

    @abstractmethod
    def run_diplomatic_mission(self, missions, characters):

        d = getattr(characters[missions['diplomatic_agent']],'diplomacy')

        intel_count = [0,1,2,3,1,2][d]

        if d > 3 :
            CharacterIntelligence.generate(target_house,target_roster,characters,self.intelligence_logs)
        else:
            RosterIntelligence.generate(target_house,target_roster,characters,self.intelligence_logs)

        # characters

        # STARK : Assitance from the Northmen - An addition Level 3 diplomatic mission is run each episode against a random House on this House's behest

        pass

    @abstractmethod
    def run_assassination_mission(self):
        pass

    def damage_dealt(self, mission):
        # MARTELL : All attacks to become lethal, provided that the total prominence power of this House is lower than the prominence of the target's roster

        # if self.roster_prominence < target.roster_prominence: 
        pass
        

    def plot_assassination(self,mission):

        # GREYJOY : Theon splatter damage. On a succesful attack by Theon, all characters of the other roster take $5\%$ damage

        # self.damage_dealt(mission)

        pass

    def foil_assassination(self,mission):
        # Chance that an attack on this House backfires and retargets the assassin itself - Chance is $15\% *$ target's prominence power

        # Check Immunity

        pass


    def reveal_outgoing_missions(self, mission):

        # Mission Type and Result

        # If Diplomacy / Succesful Attack - set to hide by default

        # If Failed Attack - set to reveal by default

        # Target player target_player.house.reveal_missions_target()

        # If Tyrell, don't call() target_player.house.reveal_missions_target()
        pass

    def reveal_incoming_missions(self, mission):
        pass

        # MEEREEN: ignore the hidden property on the diplomatic mission and reveal its 
            # Origin House

        # Update the personal Chronicle

        # ARRYN : Chance of recovering intel from the source of diplomatic missions run against this house - Chance is $50\%$, intel at same level as the mission

        # NIGHTWATCH : Dissemination of misinformation. Chance of false intel to be recovered in diplomatic missions run against this house is $50\%$


    def award_points(self, league, episode, award, scores, characters, health, missions):
        # league.award.character.points *  (6 - character.prominence) * house.bonus * roster.character.health * house.ability * character.mission.efficiency
        
        roster_score = ScoreCounter()

        for character, h in health.iteritems():

            if character not in scores:
                roster_score.update({character : 0})

            base_score = scores[character]
            prominence_multiplier = (6 - characters[character].prominence)
            house_bonus = (100 + getattr(self, award)) / 100.0
            health_penalty = h / 100.0
            mission_penalty = self.mission_efficiency(league, episode, character, characters, missions)
            
            points = reduce(operator.mul, [base_score, prominence_multiplier, house_bonus, health_penalty, mission_penalty])
            
            roster_score.update({character : points})

        return roster_score

    def mission_efficiency(self, league, episode, character, characters, missions):
        d = getattr(characters[character],'diplomacy')
        v = getattr(characters[character],'violence')

        diplomacic_penalty = league.game.diplomacy_performance_penalty[d]
        violence_penalty = league.game.violence_performance_penalty[v]

        try:
            episode_missions = [mission for mission in missions if mission['episode'] == episode.number][0]
        except IndexError:
            return 1
        
        if character == episode_missions['diplomatic_agent']:
            return 1 - character[character[character]['diplomacy']]

        if character == episode_missions['assassination_agent']:
            return 1 - character[character[character]['violence']]            


class HouseArryn(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'jockey':20}
        self.immunity = 'petyrbaelish'
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
        self.immunity = 'theongreyjoy'

        super(HouseGreyjoy, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseIndependent(House):
    def __init__(self, name):
        self.name = name
        self.immunity = 'jaqenhghar'
        self.bonus = {'style':10,'support':10}
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

    def mission_efficiency(self, league, episode, character, characters, missions):
        return 1

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
        self.immunity = 'varys'
        super(HouseMeereen, self).__init__(**self.bonus)

    def run_diplomatic_mission():
        pass

    def run_assassination_mission():
        pass


class HouseMinor(House):
    def __init__(self, name):
        self.name = name
        self.bonus = {'wit':10,'support':10}
        super(HouseMinor, self).__init__(**self.bonus)

    def award_points(self, league, episode, award, scores, characters, health, missions):
        
        roster_score = ScoreCounter()

        for character, h in health.iteritems():

            if character not in scores:
                roster_score.update({character : 0})

            base_score = scores[character]
            
            # House Ability
            prominence = characters[character].prominence
            if prominence < 3:
                prominence = prominence - 1

            prominence_multiplier = (6 - prominence)
            house_bonus = (100 + getattr(self, award)) / 100.0
            health_penalty = h / 100.0
            mission_penalty = self.mission_efficiency(league, episode, character, characters, missions)
            
            points = reduce(operator.mul, [base_score, prominence_multiplier, house_bonus, health_penalty, mission_penalty])
            
            roster_score.update({character : points})

        return roster_score

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
PLAYERS
'''

class Player(object):
    """A League Player"""
    def __init__(self, league, id, alias, alias_short, email, facebook, first_name, full_name,
                    roster_id=None, house=None, missions=None, votes=None):
        super(Player, self).__init__()
        self.id = id
        self.league = league
        self.alias = alias
        self.alias_short = alias_short
        self.email = email
        self.facebook = facebook
        self.first_name = first_name
        self.full_name = full_name
        self.roster_id = roster_id

        self.house = self.ofHouse(house)
        self.house.intelligence_logs = self.collect_intelligence()
        
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

    def collect_intelligence(self):
        return filter(lambda i: i['player'] == self.id, self.league.intelligence)

    def get_roster_prominence(self, characters):
        prominence = sum([characters[character]['prominence'] for character in self.roster.values()])
        return prominence


'''
INTELLIGENCE
'''

class Intelligence(object):
    """Intelligence

    Example : This character has more diplomacy than prominence, but less damage than both
    """
    def __init__(self):
        super(Intelligence, self).__init__()

    @classmethod
    def generate(cls, target_house, target_roster, characters, intelligence_logs,
        episode_number=None, refresh=False):
        return True

class RosterIntelligence(Intelligence):
    """RosterIngelligence

    Example : There are more Starks than Lannisters, both at least one
    """
    def __init__(self):
        super(RosterIngelligence, self).__init__()
        self.arg = arg

class CharacterIntelligence(Intelligence):
    """docstring for RosterIngelligence"""
    def __init__(self):
        super(RosterIngelligence, self).__init__()
        self.arg = arg
        

'''
UTILS
'''

class ScoreCounter(Counter):
    def __str__(self):
        scores = sorted(self.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Character','Score'],tablefmt="pipe",numalign="right")

if __name__ == "__main__":
    game = Ascension()
    
    # for league in game.leagues:
        # league.process_episode_results()

    # DEVELOPER
    for league in game.leagues:
        league.process_episode_results()