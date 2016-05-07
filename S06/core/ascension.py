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
    def __init__(self, episode=None, firebase_url = 'https://ascension.firebaseio.com'):
        super(Ascension, self).__init__()
        self.ref = firebase.FirebaseApplication(firebase_url, None)
        self.db = self.ref.get('/', None)
        
        self.awards = ['wit','damage','jockey','style','support']
        self.rank_score = {"1":20,"2": 8}
        self.diplomacy_performance_penalty = [0,0,0.25,0.5,0,0.25]
        self.violence_performance_penalty = [0,0.5,0.25,0,0.25,0.5]

        keys = ['character_health', 'character_scores', 'episode_scores', 'leaderboard', 'league_chronicles',
                'murder_log', 'player_award_scores', 'player_chronicles', 'player_intelligence',
                'player_roster_award_scores', 'players', 'rosters']

        for key in keys :
            try:
                setattr(self, key, self.db[key])
            except KeyError:
                self.db[key] = {}
                setattr(self, key, self.db[key])

        self.episodes = self.setup_episodes()

        if episode is None:
            episode = filter(lambda x : x.current, self.episodes.values())[0].number
        
        self.most_recent_episode = episode

        self.characters = self.setup_characters()
        self.leagues = self.setup_leagues()

    # Init

    def setup_episodes(self):
        return {id: Episode(**e) for (id, e) in self.db['episodes'].iteritems()}

    def setup_characters(self):
        return {id: Character(**c) for (id, c) in self.db['characters'].iteritems()}

    def setup_leagues(self):
        # DEVELOPER MODE : ONLY SHOW ESSOS DATA
        # return [League(l, self) for l in self.db['leagues'].keys() if l == 'essos']
        return [League(l, self) for l in self.db['leagues'].keys()]

    # Saving Data

    def update_character_scores(self, keys, scores):
        '''EPISODE SCORES PER CHARACTER PER AWARD

        'character_scores'
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
        self.ref.put('/character_scores/', firebase_key, scores)
        
        self.character_scores.update({firebase_key : scores})


    def update_player_roster_award_scores(self, keys, scores):
        ''' PLAYER SCORES PER CHARACTER PER AWARD

        'player_roster_award_scores':
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
        self.ref.put('/player_roster_award_scores/', firebase_key, scores)

        self.player_roster_award_scores.update({firebase_key : scores})


    def update_player_award_scores(self, keys, scores):
        '''PLAYER SCORES PER AWARD PER EPISODE

        'player_award_scores':
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
        self.ref.put('/player_award_scores/', firebase_key, scores)

        self.player_award_scores.update({firebase_key : scores})


    def update_episode_scores(self, keys, scores):
        ''' PLAYER SCORES PER EPISODE

        'episode_scores':
            <league_id><episode_id> :
                "episode" : <episode_id>,
                "league" : <league_id>,
                "scores" : 
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>

        '''
        firebase_key = "{league}{episode}".format(**keys)
        self.ref.put('/episode_scores/', firebase_key, scores)

        self.episode_scores.update({firebase_key : scores})

    def update_leaderboard(self, keys, scores):
        ''' SUM OF PLAYER EPISODE SCORES

        'leaderboard':
            <league_id><episode_id> :
                "episode" : <episode_id>,
                "league" : <league_id>,
                "scores" : 
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>
                    <player> : <score>

        '''
        firebase_key = "{league}{episode}".format(**keys)
        self.ref.put('/leaderboard/', firebase_key, scores)

        self.episode_scores.update({firebase_key : scores})


    def update_player_intelligence(self, keys, intel, append=False):
        ''' INTELLIGENCE  PER PLAYER 
        "player_ingelligence"
            <league_id>+<episode_id>+<player_id>:
                "league" : <league>
                "episode" : <episode_id>,
                "player" : <player_id>,
                "intelligence" :
                    <intel_code> :
                        "message" : <intel_msg>,
                        "code" : <intel_code>,
                        "type" : 'roster|character'
                        "target_house" : <house_id>,
                        "target_character" : <character_id>,
                        "source" : 'mission|ability|attempt'
        '''
        firebase_key = "{league}{episode}{player}".format(**keys)
        
        if append:
            for code, intel in intel['intelligence'].iteritems():
                self.ref.put('/player_intelligence/' + firebase_key + '/intelligence/', code, intel)
            
            self.player_intelligence[firebase_key]['intelligence'].update({code: intel})
            
        else:
            self.ref.put('/player_intelligence/', firebase_key, intel)
            self.player_intelligence.update({firebase_key : intel})


    def set_character_health(self, key, health):
        ''' HEALTH PER ROSTER CHARACTER 
        'character_health':
            <league_id><house_id><episode_id> :
                "episode" : <episode_id>,
                "house" : <roster_id>,
                "health" : 
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
        '''

        self.ref.put('/character_health/', key, health)


    def update_murder_log(self, keys, murders):
        """Save the Murder Log locally, no need to propagate to Firebase"""
        firebase_key = "{league}{episode}".format(**keys)
        self.murder_log.update({ firebase_key : murders })


    def update_character_health(self, keys, murder):
        ''' HEALTH PER ROSTER CHARACTER 
        'character_health':
            <league_id><house_id><episode_id> :
                "episode" : <episode_id>,
                "house" : <roster_id>,
                "health" : 
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
                    <character_id> : health
        '''

        firebase_key = "{league}{house}{episode}".format(**keys)
        prev_key = "{}{}{}".format(keys['episode'], keys['house'], str(int(keys['episode'])-1))

        # Get Previous Health
        try:
            prev_health = self.character_health[prev_key][murder['target_character']]
        except KeyError:
            prev_health = 100

        # Dock Current Damage
        new_health = prev_health - murder['damage_dealt']

        # Update Locally
        self.character_health[firebase_key]['health'].update({ murder['target_character']: new_health})
        
        # Update Firebase
        self.ref.put('/character_health/', firebase_key, self.character_health[firebase_key])


    def update_player_chronicles(self, keys, message, cat, suffix=''):
        ''' ENTRY PER PLAYER CHRONICLE 
        'player_chronicles':
        <league_id><house_id><episode_id> :
            "episode" : <episode_id>,
            "house" : <house_id,
            "entries" : 
                'diplomacy_' + <code> : 
                    'msg' : <msg>
                    'type': <type>
                'assassination' : <entry>
                'ability_' + <house_id> : <entry>
                'target_' + <character_id> : <entry>
                'foiled_' + <house_id> + <code> : <entry>
                'awards_' + <award_id> : <entry>
                'ranking' : <entry>
        '''

        firebase_key = "{league}{house}{episode}".format(**keys)

        msg = lambda m, c: {"msg" : m, "cat" : c}
        
        if suffix:
            key = '_'.join([cat, suffix])
        else:
            key = cat

        if firebase_key in self.player_chronicles:
            
            self.player_chronicles[firebase_key]['entries'].update({key: msg(message,cat)})

            # Update Firebase
            self.ref.put('/player_chronicles/' + firebase_key + '/entries/', key, msg(message,cat))
        
        else:
            section = { 
                firebase_key : {
                    "episode" : keys["episode"],
                    "house" : keys["house"],
                    "entries": {key: msg(message,cat)}
                }
            }

            self.player_chronicles.update(section)

            # Update Firebase
            self.ref.put('/player_chronicles/', firebase_key, section[firebase_key])


    def update_league_chronicles(self, keys, message, cat, suffix=''):
        ''' ENTRY PER LEAGUE CHRONICLE
        'league_chronicles':
        <league_id><episode_id> :
            "episode" : <episode_id>,
            "entries" : 
                'damage' + <house_id> + <char_id> : 
                    'msg' : <msg>,
                    'type': <type>
                'death' + <house_id> + <char_id> : <entry>
        '''

        firebase_key = "{league}{episode}".format(**keys)

        msg = lambda m, c: {"msg" : m, "cat" : c}
        
        if suffix:
            key = '_'.join([cat, suffix])
        else:
            key = cat

        entry = {key: msg(message,cat)}

        if firebase_key in self.league_chronicles:
            
            self.league_chronicles[firebase_key]['entries'].update(entry)
            
            # Update Firebase
            self.ref.put('/league_chronicles/' + firebase_key + '/entries/', key, entry[key])
        
        else:
            section = { 
                firebase_key : {
                    "episode" : keys["episode"],
                    "house" : keys["house"],
                    "entries": entry
                }
            }

            self.league_chronicles.update(section)

            # Update Firebase
            self.ref.put('/league_chronicles/', firebase_key, section[firebase_key])

    # Utils

    def print_episode_scores(self, league, episode):
        key = league + episode
        player_names = [self.players[name]['first_name'] for name in self.episode_scores[key]['scores'].keys()]
        scores = self.episode_scores[key]['scores'].values()
        episode_scores = dict(zip(player_names, scores))

        scores = sorted(episode_scores.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Player','Score'],tablefmt="pipe",numalign="right")

    
'''
GAME INFO : CHARACTERS
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
        self.health = 0

    def __repr__(self):
        numeral = [0,'I','II','III','IV','V']
        return '<{} ({}) {}/{}>'.format(self.name, numeral[self.prominence], self.diplomacy, self.violence)


'''
GAME INFO : EPISODES
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
    
    for league in game.leagues:
        league.process_episode_results()

    # DEVELOPER
    # for league in game.leagues[0:]:
        # league.process_episode_results()