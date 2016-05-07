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

        self.players_raw = filter(self.filter_player, game.db['players'].values())
        
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
        p_filtered = []
        for player in self.players_raw:
            p = player.copy()
            p['league'] = self
            p['house'] = player['house'][self.name]
            p['roster_id'] = player['games'][self.name]
            p_filtered.append(p)

        return [Player(**p) for p in p_filtered]

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

    def get_episode_title(self, epno):
        return [e.title for id, e in self.game.episodes.iteritems() if id == str(epno)][0]

    def get_episode_number(self, epno):
        return [e.episode_number for id, e in self.game.episodes.iteritems() if id == str(epno)][0]


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
        self.publish_leaderboard()
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

            self.game.update_character_scores(keys, dict(score))

    def run_weekly_diplomatic_missions(self):
        episode_missions = filter(lambda v: v['episode'] == str(self.current_episode), self.missions)

        for mission in episode_missions:
            if mission['diplomatic_agent'] and mission['diplomatic_target_house']:
                
                player = self.get_player(mission['player'])
                
                target = self.get_house_player(mission['diplomatic_target_house'])
                target_roster = target.character_health

                intel = player.house.conduct_diplomacy(self, mission, target_roster, self.game.characters, self.players)
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

            if firebase_key in self.game.player_chronicles:
                del self.game.player_chronicles[firebase_key]

            self.game.ref.delete('/player_chronicles/', firebase_key)
        
        firebase_key = "{}{}".format(self.name, self.current_episode)
        if firebase_key in self.game.league_chronicles:
            del self.game.league_chronicles[firebase_key]

        self.game.ref.delete('/league_chronicles/', firebase_key)


    def create_public_chronicle_msg(self, cat, mission):
        d = mission['data']
        agent_house = self.get_house(d['house']).full_name
        target_house = self.get_house(d['target_house']).full_name
        target_character = self.game.characters[d['target_character']].name
        # SAD HACK
        is_silent = d['house'] is 'tyrell'
        if cat is 'failed' and not is_silent:
            code = "_".join([d['house'], d['target_house']])
            msg = "<span class=\"house\">{}</span> <span class=\"failed\">FAILED</span> an assassination attempt on <span class=\"house\">{}</span>".format(agent_house, target_house)

        elif cat is 'damage':
            health = self.get_house_player(d['target_house']).character_health[d['target_character']]
            code = "_".join([d['target_house'], d['target_character']])
            msg = "A character of <span class=\"house\">{}</span> was injured, their health is at <span class=\"health\">{}/100</span>".format(target_house, health)

        elif cat is 'death':
            code = "_".join([d['target_house'], d['target_character']])
            msg = "<span class=\"house\">{}</span>  lost <span class=\"character\">{}</span> to a succesful assassination.".format(target_house, target_character)

        return code, msg

    def publish_weekly_missions_chronicle(self):

        self.refresh_chronicles()

        # Player
        # Update the personal Chronicle with the character damage they incurred.
        d_missions = self.collect_diplomatic_entries()
        a_missions = self.collect_assassination_entries()

        d_missions = self.set_visibility_layer(d_missions, 'diplomatic')
        a_missions = self.set_visibility_layer(a_missions, 'assassination')
        
        for missions in [d_missions, a_missions]:
            if missions:
                for mission in missions:

                    self.get_player(mission['data']['player']).house.spread_the_word(self, mission)
            
        # Global
        # Update the public chronicle about the failures / damages / deaths
        failed_entries, damage_entries, death_entries = self.collect_league_entries(a_missions)

        for missions in [failed_entries, damage_entries, death_entries]:
            for mission in missions:
                cat = mission['type']
                suffix, message = self.create_public_chronicle_msg(cat, mission)

                keys = {
                    "league" : self.name,
                    "episode" : self.current_episode,
                    "player" : mission['data']['player'],
                    "house" : mission['data']['house']
                }

                self.game.update_league_chronicles(keys, message, cat, suffix)

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

    def collect_league_entries(self, missions):

        get_health = lambda house, char: self.get_house_player(house).character_health[char]
        
        failed_entries = []
        damage_entries = []
        death_entries = []
        
        for mission in missions:
            
            if not mission['success'] and mission['reveal']:
                mission['type'] = 'failed'
                failed_entries.append(mission)
        
            if mission['success']:
                current_health = get_health(mission['data']['target_house'], mission['data']['target_character'])
                mission['current_health'] = current_health
            
            if mission['success'] and current_health > 0:
                mission['type'] = 'damage'
                damage_entries.append(mission)        
            
            if mission['success'] and current_health == 0:
                mission['type'] = 'death'
                death_entries.append(mission)        

        return failed_entries, damage_entries, death_entries

    def award_weekly_points(self):
        
        episode_scores = {}

        for player in self.players:

            player_roster_award_scores = {}

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
                        'episode' : self.current_episode,
                        'player' : player.id,
                        'award' : award,
                        'scores' : dict(awarded_points)
                }

                points = sum(dict(awarded_points).values())
                
                player.house.inform_player_of_award_points(self, award, points)
                
                player_roster_award_scores[award] = points

                self.game.update_player_roster_award_scores(keys, scores)

            scores = {
                'episode' : self.current_episode,
                'league' : self.name,
                'player' : keys['player'],
                "scores" : player_roster_award_scores
            }

            murder_entries = self.game.murder_log[self.name + str(self.current_episode)]

            # Get awarded for murder
            murder_bounty = sum([entry['murder']['bounty'] for entry in murder_entries])

            episode_scores[player.id] = sum(player_roster_award_scores.values()) + murder_bounty

            # DEVELOPER
            self.game.update_player_award_scores(keys, scores)

        scores = {
            'episode' : self.current_episode,
            'league' : self.name,
            "scores" : episode_scores
        }

        # DEVELOPER
        self.game.update_episode_scores(keys, scores)
        

    def publish_leaderboard(self):

        keys = {
            "league" : self.name,
            "episode" : self.current_episode,
        }

        # Select all episode score to date for current league 
        leaderboard_scores = [score['scores'] for id, score in self.game.episode_scores.iteritems() if 
            score['episode'] <= keys['episode'] and score['league'] is keys['league']]


        counter = ScoreCounter()
        map(lambda s: counter.update(s), leaderboard_scores)
       
        scores = {
            'episode' : self.current_episode,
            'league' : self.name,
            "scores" : dict(counter)
        }

        import pprint
        pprint.pprint(scores)

        self.game.update_leaderboard(keys, scores)


    def publish_weekly_ranking_chronicle(self):

        episode_ranking = self.game.episode_scores[self.name + str(self.current_episode)]
        r = episode_ranking['scores']
        for player, points in r.iteritems():
            rank = sorted(r, key=r.get, reverse=True).index(player) + 1
            self.get_player(player).house.inform_player_of_episode_score_and_rank(self, rank, points)

        leaderboard_ranking = self.game.leaderboard[self.name + str(self.current_episode)]
        r = leaderboard_ranking['scores']
        for player, points in r.iteritems():
            rank = sorted(r, key=r.get, reverse=True).index(player) + 1
            self.get_player(player).house.inform_player_of_leaderboard_score_and_rank(self,rank,points)
