from player import Player
from house import *
from utils import ScoreCounter

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
        try:
            return obj['league'] == self.name
        except KeyError:
            return False

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
        # Defaults
        for key, roster in self.rosters.iteritems():
            if key not in self.game.character_health:
                self.game.character_health[key] = dict(zip(roster, [100]*7 ))

        # TODO : Merge it into Character 
        
        return {key: roster for key, roster in self.game.character_health.iteritems() if key in self.roster_ids}

    def get_player(self, uid):
        return [p for p in self.players if p.id == uid][0]

    def get_player_roster(self, uid):
        return self.get_player(uid).roster

    def get_player_house(self, uid):
        return self.get_player(uid).house.name

    def get_house_player(self, house):
        try:
            return [p for p in self.players if p.house.name == house][0]
        except IndexError:
            import pdb; pdb.set_trace()

    def get_house_roster(self, house):
        try:
            return self.get_house_player(house).roster
        except IndexError:
            import pdb; pdb.set_trace()


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
        self.run_weekly_diplomatic_missions(episode)        
        self.run_weekly_assassion_missions(episode)
        # DEVELOPER
        self.award_weekly_points(episode)

    def score_weekly_episode(self, episode):
        episode_votes = filter(lambda v: v['episode'] == str(episode.number), self.votes)
        
        for award in self.game.awards:

            score = ScoreCounter()

            for vote in episode_votes:
                for rank, points in self.game.rank_score.iteritems():
                    character = vote['vote_' + award + "_" + rank]
                    score.update({character:points})

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
            if mission['diplomatic_agent'] and mission['diplomatic_target_house']:
                
                player = self.get_player(mission['player'])
                
                target = self.get_house_player(mission['diplomatic_target_house'])
                target_roster = target.character_health

                intel = player.house.conduct_diplomacy(mission, target_roster, self.game.characters, self.players)
                intel = target.house.counter_intelligence(self, mission, intel, self.game.characters, self.players)

                keys = {
                    "league" : self.name,
                    "episode" : episode.number,
                    "player" : player.id
                }

                intelligence = keys.copy()
                intelligence.update({"intelligence": intel})

                self.game.update_player_intelligence(keys, intelligence)


    def run_weekly_assassion_missions(self, episode):
        episode_missions = filter(lambda v: v['episode'] == str(episode.number), self.missions)

        for mission in episode_missions:
            if mission['assassination_agent'] and mission['assassination_target_house'] and mission['assassination_target_character']:
                pass

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
