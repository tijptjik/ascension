# This Python file uses the following encoding: utf-8

from abc import ABCMeta, abstractmethod
from utils import ScoreCounter, ordinal
import operator

from intelligence import *

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

    # DIPLOMACY

    def run_against_character(self, diplomacy_power):
        return diplomacy_power > 3

    def run_against_roster(self, diplomacy_power):
        return diplomacy_power < 4 

    def get_mission_target(self, missions):
        return missions['diplomatic_target_house']

    def get_intel_count(self, diplomacy_power):
        return [0,1,2,3,1,2][diplomacy_power]

    def conduct_diplomacy(self, league, missions, target_health, characters, players):
        d = getattr(characters[missions['diplomatic_agent']],'diplomacy')
        
        target_house = self.get_mission_target(missions)
        target_roster = target_health
        
        intel_count = self.get_intel_count(d)

        intelligence = {}

        if self.run_against_roster(d):
            intel = RosterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, intel_count)
            intelligence.update(intel)

        if self.run_against_character(d):
            intel = CharacterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, intel_count)
            intelligence.update(intel)

        return intelligence

    def counter_intelligence(self, league, missions, intel, characters, players):
        return intel

    def generate_random_roster(self, characters):
        return dict(zip(random.sample(characters.keys(),7), [100] * 7))

    # ASSASSINATION

    def assassination_success(self, target_character, target_roster):
        return target_character in target_roster.keys()

    def bonus_mission(self, **kwargs):
        pass

    def damage_dealt(self, agent, target_house, league):
        damages = [0, (random.random() < 0.25) * 100, 25, 50, 75, 100]
        violence = getattr(league.game.characters[agent],'violence')

        return damages[violence]

    def plot_assassination(self, league, missions, target_roster):

        target_house = missions['assassination_target_house']
        target_character = missions['assassination_target_character']
        agent = missions['assassination_agent']
       
        damage_dealt = 0
        bounty = 0
        success = self.assassination_success(target_character, target_roster)

        damage_intended = self.damage_dealt(agent, target_house, league)

        if success:
            health = target_roster[target_character]
            damage_dealt = max(health - (100 - damage_intended), 0)
            bounty = damage_dealt * 2.4

        damage_potential = {
            "target_house" : target_house,
            "target_character" : target_character,
            "damage_intended" : damage_intended,
            "damage_dealt" : damage_dealt,
            "bounty" : bounty,
            "success" : success
        }

        return damage_potential

    def foil_assassination(self, league, missions, target_roster, damage):

        # Check Immunity
        if damage['target_character'] == self.immunity:

            damage.update({
                "damage_dealt" : 0,
                "bounty": 0,
                "success" : 'immune',
            })

        return damage

    # CHRONICLE & BONUS

    def spread_the_word(self, league, mission):

        mission = self.reveal_outgoing_missions(league, mission)

        target_player = league.get_house_player(mission['data']['target_house'])
        target_player.house.reveal_incoming_missions(league, mission, self.name)

    def create_ability_msg(self, **kwargs):
        pass
 
    def create_assassination_msg(self, league, mission, target_house):
        # TODO : Add custom message for when house targeted itself.
        # TODO : Add custom message for when immune characters were targeted.
        d = mission['data']
        name = league.game.characters[d['target_character']].name
        result = ['<span class=\"failed\">FAILED</span>','<span class=\"success\">SUCCEEDED</span>'][mission['success']]

        msg = "Attack on <span class=\"character\">{}</span> of <span class=\"house\">{}</span> {} - <span class=\"health\">{}</span> damage dealt for <span class=\"points\">{}</span> points".format(name,
                       target_house, result, d["damage_dealt"], d["bounty"])
        return msg

    def create_award_msg(self, award, points, title):
        if (points).is_integer():
            points = int(points)
        msg = "Roster was awarded <span class=\"points\">{}</span> points for <span class=\"award\">{}</span> in <span class=\"episode\">{}</span>".format(points, award.upper(), title)
        return award, msg

    def create_diplomatic_msg(self, mission, target_house):
        code = mission['data']['code']
        msg = "<span class=\"pre\">Intel on <span class=\"house\">{}</span> reveals:</span> {}".format(target_house, mission['data']['message'])
        return code, msg 
    
    def create_damage_msg(self, league, mission):
        d = mission['data']

        name = league.game.characters[d['target_character']].name
        health = league.get_house_player(d['target_house']).character_health[d['target_character']]

        if (health).is_integer():
            health = int(points)

        if health > 0:
            msg = """Your grace, <span class=\"character\">{}</span> has been injured in an attack - they lost <span class=\"health\">{}</span> health and the Measter
                        reports their condition is stable, but at <span class=\"health\">{}/100</span>""".format(name,
                           d["damage_dealt"], health)
        else:
            msg = """Your grace... the move against <span class=\"character\">{}</span> could not be
                     prevented, and ... has proven fatal.""".format(name)
        
        return d['target_character'], msg

    def create_leaderboard_msg(self, rounds, rank, points, league):
        if (points).is_integer():
            points = int(points)
        msg = "After <span class=\"rounds\">{}</span> rounds in the <span class=\"league\">{}</span> league, you rank <span class=\"rank\">{}</span> with <span class=\"points\">{}</span> points.".format(
            int(rounds), league.title(), rank, points)
        return msg

    def create_ranking_msg(self, episode_title, rank, points, league):
        if (points).is_integer():
            points = int(points)
        msg = "For episode <span class=\"episode\">{}</span> you ranked <span class=\"rank\">{}</span> in the <span class=\"league\">{}</span> league, with <span class=\"points\">{}</span> points.".format(
            episode_title, league.title(), rank, points)
        return msg

    def create_torture_msg(self, code, target_house, msg):
        msg = "<span class=\"pre\">Torturing <span class=\"house\">{}</span>'s assassin reveals :</span> {}".format(target_house, msg)
        return code, msg 

    def reveal_outgoing_missions(self, league, mission):

        cat = mission['type']
        suffix = ''
        target_house_name = league.get_house(mission['data']['target_house']).full_name

        if cat == 'diplomatic':
            suffix, message = self.create_diplomatic_msg(mission, target_house_name)
        if cat == 'assassination':
            message = self.create_assassination_msg(league, mission, target_house_name)

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "house" : self.name
        }

        league.game.update_player_chronicles(keys, message, cat, suffix)

        return mission

    def reveal_incoming_missions(self, league, mission, agent_house):

        cat = mission['type']

        # Failed Assassination Attempt
    
        if cat == 'assassination' and mission['reveal']:
        
            # You receive two items of Roster Intelligence from torturing your assassin.
            
            if not mission['success']:
                target_roster = league.get_house_player(agent_house).character_health
                intelligence = {}

                intel = RosterIntelligence.generate(agent_house, target_roster,
                                                    league.game.characters, self.intelligence_logs, 2)

                intelligence.update(intel)

                keys = {
                    "league" : league.name,
                    "episode" : league.current_episode,
                    "player" : league.get_house_player(self.name).id,
                    "house" : self.name
                }

                intelligence = keys.copy()
                intelligence.update({"intelligence": intel, 'agent': mission['data']['agent']})

                league.game.update_player_intelligence(keys, intelligence)

                target_house_name = league.get_house_player(agent_house).house.full_name
                for code, i in intel.iteritems():
                    cat = 'foiled'
                    suffix, message = self.create_torture_msg(code, target_house_name, i['message'])
                    suffix = "_".join([agent_house, suffix])

                    league.game.update_player_chronicles(keys, message, cat, suffix)

                # The player you attacked also receives the assassin’s Prominence and Violence Power.

                assassin = league.game.characters[mission['data']['agent']]
                a_msg = "The assassin was sent by {}, has Prominence Power {}, and Violence Power {} - They escaped... but we've set the hounds on them...".format(
                        target_house_name, assassin.prominence, assassin.violence)

                suffix, message = self.create_torture_msg('torture_'+agent_house, target_house_name, a_msg)

                league.game.update_player_chronicles(keys, message, cat, suffix)

            else:

                cat = 'target'

                keys = {
                    "league" : league.name,
                    "episode" : league.current_episode,
                    "player" : league.get_house_player(self.name).id,
                    "house" : self.name
                }

                suffix, message = self.create_damage_msg(league, mission)

                league.game.update_player_chronicles(keys, message, cat, suffix)
    
    def inform_player_of_award_points(self, league, award, points):
        cat = 'awards'

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        title = league.get_episode_title(league.current_episode)
        suffix, message = self.create_award_msg(award, points, title)

        league.game.update_player_chronicles(keys, message, cat, suffix)

    def inform_player_of_episode_score_and_rank(self, league, rank, episode_points):
        cat = 'ranking'
        suffix = ''

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        episode_title = league.get_episode_title(league.current_episode)
        rank = ordinal(rank)

        message = self.create_ranking_msg(episode_title, rank, episode_points, league.name)
        
        league.game.update_player_chronicles(keys, message, cat)

    def inform_player_of_leaderboard_score_and_rank(self, league, rank, episode_points):
        cat = 'ranking'
        suffix = ''

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        epno = league.get_episode_number(league.current_episode)
        rank = ordinal(rank)

        message = self.create_leaderboard_msg(epno, rank, episode_points, league.name)
        
        league.game.update_player_chronicles(keys, message, cat)

    # SCORING

    def deduct_auto_vote(self, league, character, prominence_multiplier, award):
        if character != self.immunity:
            return 0
        
        player = league.get_house_player(self.name).id
        votes = league.get_player_episode_votes(player)
        if votes:
            for rank, points in league.game.rank_score.iteritems():
                if votes["_".join(['vote',award,rank])] == character:
                    return points * prominence_multiplier
        return 0

    def award_points(self, league, episode, award, scores, characters, health, missions):
        
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
            points -= self.deduct_auto_vote(league, character, prominence_multiplier, award) 

            roster_score.update({character : points})

        return roster_score

    def mission_efficiency(self, league, episode, character, characters, missions):
        d = getattr(characters[character],'diplomacy')
        v = getattr(characters[character],'violence')

        diplomacic_penalty = league.game.diplomacy_performance_penalty[d]
        violence_penalty = league.game.violence_performance_penalty[v]

        try:
            episode_missions = [mission for mission in missions if mission['episode'] == episode][0]
        except IndexError:
            return 1
        
        if character == episode_missions['diplomatic_agent']:
            return 1 - character[character[character]['diplomacy']]

        if character == episode_missions['assassination_agent']:
            return 1 - character[character[character]['violence']]  


# HOUSES IN GAME OF THRONES


class HouseArryn(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Arryn'
        self.bonus = {'jockey':20}
        super(HouseArryn, self).__init__(**self.bonus)
        self.immunity = 'petyrbaelish'

    def create_ability_msg(self, intel, target_house):
        code = intel['code']
        msg = "<span class=\"pre\">Ohhh... but <span class=\"house\">{}</span> were seen. Counter intelligence reveals:</span> {}".format(target_house, intel['message'])
        return code, msg 

    def counter_intelligence(self, league, missions, intel, characters, players):

        # ARRYN ABILITY 
        # Chance of recovering intel from the source of diplomatic missions run against this house - Chance is $50\%$, intel at same level as the mission

        if random.random() < 0.5:
        # DEVELOPER
        # if random.random() < 1:

            target_health = league.get_player(missions['player']).character_health

            missions.update({
                'assassination_agent':'',
                'assassination_target_character':'',
                'assassination_target_house':'',
                'diplomatic_target_house': league.get_player_house(missions['player']),
                'player': league.get_house_player(self.name).id
                })

            arryn_intel = self.conduct_diplomacy(league, missions, target_health, characters, players)

            keys = {
                "league" : league.name,
                "episode" : league.current_episode,
                "player" : league.get_house_player(self.name).id
            }

            intelligence = keys.copy()
            intelligence.update({"intelligence": arryn_intel, 'agent': 'Arryn Ability'})

            league.game.update_player_intelligence(keys, intelligence, append=True)

            target_house = league.get_player(missions['player']).house.full_name

            for code, a_intel in arryn_intel.iteritems():
                cat = 'ability'
                
                suffix, message = self.create_ability_msg(a_intel, target_house)

                keys = {
                    "league" : league.name,
                    "episode" : league.current_episode,
                    "player" : league.get_house_player(self.name).id,
                    "house" : self.name
                }

                league.game.update_player_chronicles(keys, message, cat, suffix)

        return intel

class HouseBolton(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Bolton'
        self.bonus = {'damage':10,'support':10}
        super(HouseBolton, self).__init__(**self.bonus)

    def create_ability_msg(self, target_house_name):
        code = target_house_name
        msg = """Ramsay's dogs had their way with a visiting assassin. I doubt they'll be coming back."""
        return code, msg 

    def foil_assassination(self, league, missions, target_roster, damage):
        
        # BOLTON ABILITY 

        # Chance that an attack on this House backfires and retargets the assassin itself
        # Chance is 15% * target's prominence power

        v = getattr(league.game.characters[missions['assassination_target_character']],'prominence')

        agent = missions['assassination_agent']
        damages = [0, (random.random() < 0.25) * 100, 25, 50, 75, 100]
        violence = getattr(league.game.characters[agent],'violence')
        
        health = league.get_player(missions['player']).character_health[agent]
        damage_dealt = max(health - (100 - damages[violence]), 0)

        # Don't do any damage to immune characters
        if league.get_player_house_immunity(missions['player']) == agent:
            damage_dealt = 0        

        # DEVELOPER 
        if random.random() > v/(100/15.0):

            damage.update({
                "target_house" : league.get_player_house(missions['player']),
                "target_character" : missions['assassination_agent'],
                "damage_intended" : damages[violence],
                "damage_dealt" : damage_dealt,
                "bounty" : 0,
                "success" : True
            })


        # Update the personal Chronicles

        cat = 'ability'

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        target_house_name = league.get_player_house(missions['player'])

        suffix, message = self.create_ability_msg(target_house_name)

        league.game.update_player_chronicles(keys, message, cat, suffix)

        return damage


class HouseGreyjoy(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Greyjoy'
        self.bonus = {'damage': 20}
        super(HouseGreyjoy, self).__init__(**self.bonus)
        self.immunity = 'theongreyjoy'


    def bonus_mission(self, league, mission, target_house, target_house_name, target_roster):

        # TODO GREYJOY ABILITY

        # Theon splatter damage. On a succesful attack by Theon,
        # all characters of the other roster take $5\%$ damage
        print 'WARNING >>> THEON NEEDS SPLATTER DAMAGE'


    def spread_the_word(self, league, mission):

        mission = self.reveal_outgoing_missions(league, mission)

        if mission['type'] == 'assassination' and mission['success'] and mission['data']['agent'] == self.immunity:
            
            target_house = mission['data']['target_house']
            target_house_name = league.get_house(mission['data']['target_house']).full_name
            target_roster =  league.get_house(mission['data']['target_house']).character_health

            self.bonus_mission(league, mission, target_house, target_house_name, target_roster)

        target_player = league.get_house_player(mission['data']['target_house'])
        target_player.house.reveal_incoming_missions(league, mission, self.name)


class HouseIndependent(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'Independents'
        self.bonus = {'style':10,'support':10}
        super(HouseIndependent, self).__init__(**self.bonus)
        self.immunity = 'jaqenhghar'

    def create_ability_msg(self, target_house, faceless_name):
        code = target_house
        msg = """I've seen a man who could change his face,
            the way that other men change their clothes.
            This one looks like <span class=\"character\">{}</span>,
            and has joined our roster.""".format(faceless_name)
        return code, msg 

    def bonus_mission(self, league, mission, target_house, target_house_name, target_roster):

        # INDEPENDENT ABILITY:

        # The faceless man the ability to take on other personas.
        # If Jaqen kills a Character, they join this House's Roster

        key = "{}{}{}".format(league.name, self.name, league.current_episode)

        health = league.game.character_health[key]
        roster = health['health']
        faceless = mission['data']['target_character']


        roster.update({faceless : 100})
        
        league.game.set_character_health(key, health)

        # Update the personal Chronicles

        cat = 'ability'

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        faceless_name = league.game.characters[faceless].name

        suffix, message = self.create_ability_msg(target_house_name, faceless_name)

        league.game.update_player_chronicles(keys, message, cat, suffix)


    def spread_the_word(self, league, mission):

        mission = self.reveal_outgoing_missions(league, mission)
        
        target_house = mission['data']['target_house']
        target_player = league.get_house_player(target_house)

        if mission['type'] == 'assassination' and mission['success'] and mission['data']['agent'] == self.immunity:
            self.bonus_mission(league, mission, target_house, target_player.full_name, target_player.character_health)

        target_player.house.reveal_incoming_missions(league, mission, self.name)
 

class HouseLannister(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Lannister'
        self.bonus = {'wit':10,'jockey':10}
        super(HouseLannister, self).__init__(**self.bonus)

    def mission_efficiency(self, league, episode, character, characters, missions):
        return 1


class HouseMartell(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Martell'
        self.bonus = dict(wit=5, damage=5, jockey=5, style=5, support=5)
        super(HouseMartell, self).__init__(**self.bonus)

    def create_ability_msg(self, target_house, target_house_name):
        code = target_house
        msg = """Dorne will be subjugated no more! <span class=\"house\">{}</span>
            flaunted their power, and for that we killed them.""".format(target_house_name)
        return code, msg 

    def damage_dealt(self, agent, target_house, league):

        # MARTELL ABILITY :

        #  All attacks to become lethal, provided that the total prominence power
        #  of this House is lower than the prominence of the target's roster
        martell_prominence = league.get_house_player(self.name).roster_prominence
        target_prominence  = league.get_house_player(target_house).roster_prominence

        if martell_prominence < target_prominence:

            # Update the personal Chronicles

            cat = 'ability'

            keys = {
                "league" : league.name,
                "episode" : league.current_episode,
                "player" : league.get_house_player(self.name).id,
                "house" : self.name
            }

            target_house_name = league.get_house(target_house).full_name
            suffix, message = self.create_ability_msg(target_house, target_house_name)

            league.game.update_player_chronicles(keys, message, cat, suffix)

            return 100
        else:
            damages = [0, (random.random() < 0.25) * 100, 25, 50, 75, 100]
            violence = getattr(league.game.characters[agent],'violence')
            
            return damages[violence]


class HouseMeereen(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'Council of Meereen'
        self.bonus = {'wit':20}
        super(HouseMeereen, self).__init__(**self.bonus)
        self.immunity = 'varys'

    def create_ability_msg(self, target_house, target_house_name):
        code = target_house
        msg = "How transparent. <span class=\"house\">{}</span> ran a diplomatic mission against us.".format(target_house_name)
        return code, msg

    def reveal_incoming_missions(self, league, mission, agent_house):
        cat = mission['type']

        # Failed Assassination Attempt

        if cat == 'assassination' and mission['reveal']:
        
            # You receive two items of Roster Intelligence from torturing your assassin.
            
            if not mission['success']:
                target_roster = league.get_house_player(agent_house).character_health
                intelligence = {}

                intel = RosterIntelligence.generate(agent_house, target_roster,
                                                    league.game.characters, self.intelligence_logs, 2)

                intelligence.update(intel)

                keys = {
                    "league" : league.name,
                    "episode" : league.current_episode,
                    "player" : league.get_house_player(self.name).id,
                    "house" : self.name
                }

                intelligence = keys.copy()
                intelligence.update({"intelligence": intel, 'agent': mission['data']['agent']})

                league.game.update_player_intelligence(keys, intelligence)

                target_house_name = league.get_house_player(agent_house).house.full_name
                for code, i in intel.iteritems():
                    cat = 'foiled'
                    suffix, message = self.create_torture_msg(code, target_house_name, i['message'])
                    suffix = "_".join([agent_house, suffix])

                    league.game.update_player_chronicles(keys, message, cat, suffix)

                # The player you attacked also receives the assassin’s Prominence and Violence Power.

                assassin = league.game.characters[mission['data']['agent']]
                a_msg = "The assassin was sent by {}, has Prominence Power {}, and Violence Power {} - They escaped... but we've set the hounds on them...".format(
                        target_house_name, assassin.prominence, assassin.violence)

                suffix, message = self.create_torture_msg('torture_'+agent_house, target_house_name, a_msg)

                league.game.update_player_chronicles(keys, message, cat, suffix)

            else:

                cat = 'target'

                keys = {
                    "league" : league.name,
                    "episode" : league.current_episode,
                    "player" : league.get_house_player(self.name).id,
                    "house" : self.name
                }

                suffix, message = self.create_damage_msg(league, mission)

                league.game.update_player_chronicles(keys, message, cat, suffix)

        # MEEREEN: ignore the hidden property on the diplomatic mission and reveal its 

        elif cat == 'diplomatic':

            cat = 'ability'

            keys = {
                "league" : league.name,
                "episode" : league.current_episode,
                "player" : league.get_house_player(self.name).id,
                "house" : self.name
            }

            target_house_name = league.get_house(agent_house).full_name
            suffix, message = self.create_ability_msg(agent_house, target_house_name)

            league.game.update_player_chronicles(keys, message, cat, suffix)



class HouseMinor(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'League of Minor Houses'
        self.bonus = {'wit':10,'support':10}
        super(HouseMinor, self).__init__(**self.bonus)

    def award_points(self, league, episode, award, scores, characters, health, missions):
        
        roster_score = ScoreCounter()

        for character, h in health.iteritems():

            if character not in scores:
                roster_score.update({character : 0})

            base_score = scores[character]
            
            # MINOR Ability
            prominence = characters[character].prominence
            if prominence < 3:
                prominence = prominence - 1

            prominence_multiplier = (6 - prominence)
            house_bonus = (100 + getattr(self, award)) / 100.0
            health_penalty = h / 100.0
            mission_penalty = self.mission_efficiency(league, episode, character, characters, missions)
            
            points = reduce(operator.mul, [base_score, prominence_multiplier,
                                                house_bonus, health_penalty, mission_penalty])
            
            roster_score.update({character : points})

        return roster_score


class HouseNightswatch(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'Nightswatch & Free Folk'
        self.bonus = {'damage':10,'support':10}
        super(HouseNightswatch, self).__init__(**self.bonus)

    def create_ability_msg(self, agent_house):
        code = agent_house
        msg = """Whatever truth lies beyond the wall. Their spies will never know.
            Sent out false intel to visiting diplomatic mission."""
        return code, msg 

    def counter_intelligence(self, league, missions, intel, characters, players):

        # NIGHTWATCH ABILITY

        # Dissemination of misinformation. Chance of false intel to be recovered in
        # diplomatic missions run against this house is 50%

        if random.random() < 0.5:
            
            false_roster = self.generate_random_roster(characters)
            intel = self.conduct_diplomacy(league, missions, false_roster, characters, players)          

            # Update the personal Chronicles

            cat = 'ability'

            keys = {
                "league" : league.name,
                "episode" : league.current_episode,
                "player" : league.get_house_player(self.name).id,
                "house" : self.name
            }

            agent_house = league.get_player_house(missions['player'])
            suffix, message = self.create_ability_msg(agent_house)

            league.game.update_player_chronicles(keys, message, cat, suffix)
            
        return intel

class HouseStark(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Stark'
        self.bonus = {'support':20}
        super(HouseStark, self).__init__(**self.bonus)

    def create_ability_msg(self, target_house, target_house_name):
        code = target_house
        msg = "For the North! Our spies returned with news on <span class=\"house\">{}</span>.".format(target_house_name)
        return code, msg

    def conduct_diplomacy(self, league, missions, target_health, characters, players):
        d = getattr(characters[missions['diplomatic_agent']],'diplomacy')
        
        target_house = self.get_mission_target(missions)
        target_roster = target_health
        
        intel_count = self.get_intel_count(d)

        intelligence = {}

        if self.run_against_roster(d):
            intel = RosterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, intel_count)
            intelligence.update(intel)

        if self.run_against_character(d):
            intel = CharacterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, intel_count)
            intelligence.update(intel)

        # STARK ABILITY

        other_players = [p for p in players if p.house.name != self.name]
        northman_target = random.sample(other_players, 1)[0]

        target_house = northman_target.house.name
        target_roster = northman_target.character_health
        intel = RosterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, 3)
        intelligence.update(intel)

        # Add Entry to Player's personal Chronicle
        cat = 'ability'

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        target_house_name = league.get_house(target_house).full_name
        suffix, message = self.create_ability_msg(target_house, target_house_name)

        league.game.update_player_chronicles(keys, message, cat, suffix)

        return intelligence


class HouseTargaryen(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Targaryen'
        self.bonus = {'damage':10,'jockey':10}
        super(HouseTargaryen, self).__init__(**self.bonus)

    def is_dothraki(self, league, agent):
        assassin = league.game.characters[agent]
        return 'Dothraki' in assassin.bio

    def bonus_mission(self, league, mission, target_house, target_house_name, target_roster):

        # TODO TARGARYEN ABILITY:

        # All Characters on this House’s Roster gain
        # 5% Bonus on a succesful attack by a Dothraki Character

        print 'WARNING >>> TARGARYEN NEEDS HOUSE ABILITY'

    def spread_the_word(self, league, mission):

        mission = self.reveal_outgoing_missions(league, mission)

        if mission['type'] == 'assassination' and mission['success'] and self.is_dothraki(league, mission['data']['agent']):

            target_house = mission['data']['target_house']
            target_house_name = league.get_house(mission['data']['target_house']).full_name
            target_roster =  league.get_house(mission['data']['target_house']).character_health

            self.bonus_mission(league, mission, target_house, target_house_name, target_roster)

        target_player = league.get_house_player(mission['data']['target_house'])
        target_player.house.reveal_incoming_missions(league, mission, self.name)
 


class HouseTyrell(House):
    def __init__(self, name):
        self.name = name
        self.full_name = "House Tyrell"
        self.bonus = {'style':20}
        super(HouseTyrell, self).__init__(**self.bonus)

    def create_ability_msg(self, target_house, target_house_name):
        code = target_house
        msg = "For the North! Our spies returned with news on {}.".format(target_house_name)
        return code, msg

    def spread_the_word(self, league, mission):

        self.reveal_outgoing_missions(league, mission)

        # TYRELL ABILITY : don't call() target_player.house.reveal_incoming_missions()

        # Add Entry to Player's personal Chronicle

        cat = 'ability'

        target_house = mission['data']['target_house']

        if mission['type'] == 'assassination' and not mission['success']:
            agent = league.game.characters[mission['data']['agent']].name
            message = "The assassination attempt may have failed - but at least {} got away without being noticed.".format(agent)
            
        elif mission['type'] == 'diplomatic' and target_house == 'meereen':
            message = "Council of Meereen... their little birds have sung their last song"

        else:
            message = "We moved through the shadows and remained unseen."

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "player" : league.get_house_player(self.name).id,
            "house" : self.name
        }

        league.game.update_player_chronicles(keys, message, cat, target_house)
