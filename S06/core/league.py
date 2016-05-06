from player import Player
from house import *
from utils import ScoreCounter, ordinal
from collections import defaultdict

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

        self.current_episode = game.most_recent_episode
        self.current_episode_score = {}

        self.character_health = self.collect_character_health()

        self.assign_rosters_to_players()
    

    # Helper Methods

    def __repr__(self):
        return '<{0} League>'.format(self.name.title())

    def filter_player(self, player):
        return 'games' in player and type(player['games']) is not bool and self.name in player['games']

    def filter_league(self, obj):
        try:
            return obj['league'] == self.name
        except KeyError:
            return False

    def filter_intel(self, intel):
        return intel['episode'] is self.current_episode and intel['league'] is self.name

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
        return {roster_id: roster.values() for roster_id, roster in self.game.rosters.iteritems() if roster_id in self.roster_ids}

    def collect_character_health(self):
        """ HEALTH FOR ROSTER CHARACTER IN LEAGUE
        character_health.
            <house_id>.
                <character_id> : health
        """

        for roster_id, roster in self.rosters.iteritems():
            house = self.get_roster_house(roster_id)
            key = "{}{}{}".format(self.name, house, self.current_episode)
            prev_key = "{}{}{}".format(self.name, house, str(int(self.current_episode)-1))

            # GET CHAR_HEALTH FROM PREVIOUS EPISODE AND SET IT AS THE CURRENT
            if prev_key in self.game.character_health:
                self.game.character_health[key] = self.game.character_health[prev_key]
            else:
                # IF NO CHAR_HEALTH, GENERATE DEFAULT
                health = {
                    "episode" : self.current_episode,
                    "house" : house,
                    "roster" : roster_id,
                    "health" : dict(zip(roster, [100]*len(roster) ))
                }
                self.game.character_health[key] = health
                self.game.set_character_health(key, health)

        # TODO : Merge it into Character 
        
        return {h['house']: h['health'] for key, h in self.game.character_health.iteritems() if h['roster'] in self.roster_ids}

    def get_player(self, uid):
        return [p for p in self.players if p.id == uid][0]

    def get_house(self, hid):
        return [p.house for p in self.players if p.house.name == hid][0]

    def get_player_roster(self, uid):
        return self.get_player(uid).roster

    def get_player_house(self, uid):
        return self.get_player(uid).house.name

    def get_house_player(self, house):
        return [p for p in self.players if p.house.name == house][0]

    def get_house_roster(self, house):
        return self.get_house_player(house).roster

    def get_roster_house(self, rid):
        return [p.house.name for p in self.players if p.roster_id == rid][0]

    def assign_rosters_to_players(self):
        for player in self.players:
            player.roster = self.rosters[player.roster_id]
            player.character_health = self.character_health[player.house.name]
            player.roster_prominence = player.get_roster_prominence(self.game.characters)

    # Weekly Processes

    def process_episode_results(self):
        self.score_weekly_episode()
        self.run_weekly_diplomatic_missions()        
        self.run_weekly_assassion_missions()
        self.publish_weekly_missions_chronicle()
        # DEVELOPER
        self.award_weekly_points()
        self.publish_weekly_ranking_chronicle()

    def score_weekly_episode(self):
        episode_votes = filter(lambda v: v['episode'] == str(self.current_episode), self.votes)
        
        for award in self.game.awards:

            score = ScoreCounter()

            for vote in episode_votes:
                for rank, points in self.game.rank_score.iteritems():
                    character = vote['vote_' + award + "_" + rank]
                    score.update({character:points})

            keys = {
                "league" : self.name,
                "episode" : self.current_episode,
                "award" :  award
            }

            self.current_episode_score[award] = score

            self.game.update_episode_scores(keys, dict(score))

    def run_weekly_diplomatic_missions(self):
        episode_missions = filter(lambda v: v['episode'] == str(self.current_episode), self.missions)

        for mission in episode_missions:
            if mission['diplomatic_agent'] and mission['diplomatic_target_house']:
                
                player = self.get_player(mission['player'])
                
                target = self.get_house_player(mission['diplomatic_target_house'])
                target_roster = target.character_health

                intel = player.house.conduct_diplomacy(mission, target_roster, self.game.characters, self.players)
                intel = target.house.counter_intelligence(self, mission, intel, self.game.characters, self.players)

                keys = {
                    "league" : self.name,
                    "episode" : self.current_episode,
                    "player" : player.id
                }

                intelligence = keys.copy()
                intelligence.update({"intelligence": intel, 'agent': mission['diplomatic_agent']})

                self.game.update_player_intelligence(keys, intelligence)


    def run_weekly_assassion_missions(self):
        episode_missions = filter(lambda v: v['episode'] == str(self.current_episode), self.missions)

        murder_set = []

        for mission in episode_missions:
            if mission['assassination_agent'] and mission['assassination_target_house'] and mission['assassination_target_character']:

                player = self.get_player(mission['player'])
                
                target = self.get_house_player(mission['assassination_target_house'])
                target_roster = target.character_health

                # self.game.characters, self.players
                damage_potential = player.house.plot_assassination(self, mission, target_roster)
                damage_actual = target.house.foil_assassination(self, mission, target_roster, damage_potential)  

                keys = {
                    "league" : self.name,
                    "episode" : self.current_episode,
                    "player" : player.id,
                    "house" : player.house.name
                }

                murder = keys.copy()
                murder.update({"murder": damage_actual, 'agent': mission['assassination_agent']})

                murder_set.append(murder)

        # Award points for succesful assassinations
        
        if murder_set:
            
            import pprint
            pprint.pprint([murder for murder in murder_set if murder['murder']['success']])

            # Dock Character Health 

            murder_set = self.uncover_conspiracies(murder_set)

            self.process_murder_log(murder_set)

 
        # INDEPENDENT : The faceless man the ability to take on other personas. If Jaqen kills a Character, they join this House's Roster

        # TARGARYAN : All Characters on this House's Roster gain $5\%$ Bonus on a succesful attack by a Dothraki Character

        

        

    def uncover_conspiracies(self, murder_set):
        # Points are split between the number of assailants.
        # If a stronger assassin targets the same characters

        conspiracies = defaultdict(list)
        map(lambda m: conspiracies[(m['murder']['target_house'],m['murder']['target_character'])].append(m),  murder_set)
        for pair, murders in conspiracies.iteritems():
            max_bounty = 0
            conspirators = []
            if len(murders) > 1:
                for murder in murders:
                    if murder['murder']['bounty'] > max_bounty:
                        for conspirator in conspirators:
                            conspirator['murder'].update({'bounty':0,'damage_dealt':0,'success':'outwitted'})
                        conspirators = [murder]
                    elif murder['murder']['bounty'] == max_bounty:
                        conspirators.append(murder)
                    else:
                        murder['murder'].update({'bounty':0,'damage_dealt':0,'success':'outwitted'})

                for conspirator in conspirators:
                    bounty = conspirator['murder']['bounty']
                    conspirator['murder'].update({'bounty': bounty/len(conspirators)})

        murder_set = [val for sublist in conspiracies.values() for val in sublist]
        
        return murder_set

    def process_murder_log(self, murder_set):
        
        self.game.update_murder_log({'league':self.name,'episode':self.current_episode}, murder_set)
        
        succesful_murders = [murder for murder in murder_set if murder['murder']['success']]

        for murder in succesful_murders:

            keys = murder.copy()
            keys.update({
                'house' : murder['murder']['target_house']
                })
  
            self.game.update_character_health(keys, murder['murder'])


    def refresh_chronicles(self):
        houses = [p.house.name for p in self.players]
        for house in houses:

            firebase_key = "{}{}{}".format(self.name, house, self.current_episode)

            self.game.ref.delete('/player_chronicles/', firebase_key)

    def publish_weekly_missions_chronicle(self):

        self.refresh_chronicles()

        # Player
        d_missions = self.collect_diplomatic_entries()
        a_missions = self.collect_assassination_entries()

        d_missions = self.set_visibility_layer(d_missions, 'diplomatic')
        a_missions = self.set_visibility_layer(a_missions, 'assassination')
        
        for missions in [d_missions, a_missions]:
            if missions:
                for mission in missions:

                    self.get_player(mission['data']['player']).house.spread_the_word(self, mission)
                    # Update the personal Chronicle with the character damage they incurred.
            
        # Global
        # Update the public chronicle about the deaths / damage
        failed_entries = self.collect_failed_entries()
        damage_entries = self.collect_damage_entries()
        death_entries = self.collect_death_entries()

        for missions in [failed_entries, damage_entries, death_entries]:
            for mission in missions:
                # self.get_player(mission['data']['player']).house.spread_the_word(self, mission)
                pass


    def set_visibility_layer(self, data, mission_type):
        if data:
            logs = map(lambda d: {"type": mission_type, "success": True, "reveal": False, "data" : d}, data)
            if mission_type == 'assassination':
                for log in logs:
                    if not log['data']['success']:
                        log['success'] = False
                        log['reveal'] = True
            return logs

    def collect_diplomatic_entries(self):
        """ essos51facebook:10100288986712842
            {
              "episode" : 51,
              "intelligence" : {
                "C|NI|MARI|E|N|P" : {
                  "code" : "C|NI|MARI|E|N|P",
                  "message" : "Character has the lowest Prominence Power on the target roster",
                  "target_character" : "marei",
                  "target_house" : "nightswatch",
                  "type" : "character"
                }
              },
              "league" : "essos",
              "player" : "facebook:10100288986712842",
              "agent"  : "varys" 
            }
        """
        player_entries = [i for k, i in self.game.player_intelligence.iteritems() if self.filter_intel(i)]

        entries = []
        for entry in player_entries:
            for k, v in entry['intelligence'].iteritems():
                v['player'] = entry['player']
                v['agent'] = entry['agent']
                entries.append(v)

        return entries

    def collect_assassination_entries(self):
        """
        [{'episode': 51,
          'house': u'independent',
          'league': u'essos',
          'murder': {'bounty': 0,
                     'damage_dealt': 100,
                     'damage_intended': 100,
                     'success': True,
                     'target_character': u'aryastark',
                     'target_house': u'independent'},
          'player': u'facebook:10100288986712842'}]

        """
        try:
            murder_entries = self.game.murder_log[self.name + str(self.current_episode)]
        except KeyError:
            return []

        entries = []
        for entry in murder_entries:
            e = entry['murder']
            e['player'] = entry['player']
            e['house'] = entry['house']
            e['agent'] = entry['agent']
            entries.append(e)

        return entries

    def collect_failed_entries(self):

        #  It will be published in the Chronicle that you made an attempt and failed, mentioning your house, and the house you were targeting.
        # 'global' : true if
            # type:assassination and success:false and reveal:true

        entries = []
        return entries

    def collect_damage_entries(self):
        entries = []
        return entries

    def collect_death_entries(self):
        entries = []
        return entries

    def award_weekly_points(self):
        
        leaderboard_scores = {}

        for player in self.players:

            player_episode_scores = {}

            for award in self.game.awards:
                
                award_score = self.current_episode_score[award]
                awarded_points = player.house.award_points(self, self.current_episode, award,
                    award_score, self.game.characters, player.character_health, player.missions)
                
                keys = {
                    "league" : self.name,
                    "episode" : self.current_episode,
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


    def publish_weekly_ranking_chronicle(self):
        pass
        # entries = self.collect_ranking_entries()
        # for entry in entries:
        #     keys = ''
        #     message = ''
        #     cat = ''
        #     suffix = ''

        #     self.game.update_player_chronicles(entry)

    def collect_ranking_entries(self):
        tmpl = lambda k : "With {score} points, after {episode_number} Episodes, you rank {rank} in the {league} League.".format(**k)
        pass

