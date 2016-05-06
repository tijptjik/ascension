# This Python file uses the following encoding: utf-8

from abc import ABCMeta, abstractmethod
from utils import ScoreCounter
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

    def conduct_diplomacy(self, missions, target_health, characters, players):
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

    def bonus_mission(self, league, missions, target_roster):
        pass

    def plot_assassination(self, league, missions, target_roster):

        target_house = missions['assassination_target_house']
        target_character = missions['assassination_target_character']
        agent = missions['assassination_agent']
       
        damage_dealt = 0
        bounty = 0
        success = self.assassination_success(target_character, target_roster)

        damage_intended = self.damage_dealt(agent, target_house, league)

        if success:
            import pdb; pdb.set_trace()
            health = target_roster['target_character']
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

        if success:
            bonus_mission(self, league, missions, target_roster)

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


    def damage_dealt(self, agent, target_house, league):
        damages = [0, (random.random() < 0.25) * 100, 25, 50, 75, 100]
        violence = getattr(league.game.characters[agent],'violence')

        return damages[violence]


    def damage_bonus(self, league, mission, target_roster, damage_actual):

        # INDEPENDENT : The faceless man the ability to take on other personas. If Jaqen kills a Character, they join this House's Roster

        # TARGARYAN : All Characters on this House's Roster gain $5\%$ Bonus on a succesful attack by a Dothraki Character

        pass



    def spread_the_word(self, league, mission):

        mission = self.reveal_outgoing_missions(league, mission)

        target_player = league.get_house_player(mission['data']['target_house'])
        target_player.house.reveal_incoming_missions(league, mission)

        # TYRELL : don't call() target_player.house.reveal_incoming_missions()

        # INDEPENDENT : The faceless man the ability to take on other personas. If Jaqen kills a Character, they join this House's Roster

    
    def create_torture_msg(self, code, target_house, msg):
        msg = "Torturing {}'s assassin reavels : {}".format(target_house, msg)
        return code, msg 
            
    def create_diplomatic_msg(self, mission, target_house):
        code = mission['data']['code']
        msg = "Intel on {} reveals: {}".format(target_house,mission['data']['message'])
        return code, msg 

    def create_assassination_msg(self, mission, target_house):
        d = mission['data']
        result = ['FAILED','SUCCEEDED'][mission['success']]
        message = "Attack on {} of {} {} - {} damage dealt for {} points".format(d['target_character'],
                       target_house, result, d["damage_dealt"], d["bounty"])
        return message

    def reveal_outgoing_missions(self, league, mission):
        """ VISIBILITY LAYER
        'type' : 'diplomatic|assassination'
        'success' : true|false
        'reveal' : true|false
        'data' : {}
        """

        cat = mission['type']
        suffix = ''
        target_house = league.get_house(mission['data']['target_house']).full_name

        if cat == 'diplomatic':
            suffix, message = self.create_diplomatic_msg(mission, target_house)
        if cat == 'assassination':
            message = self.create_assassination_msg(mission, target_house)

        keys = {
            "league" : league.name,
            "episode" : league.current_episode,
            "house" : self.name
        }

        league.game.update_player_chronicles(keys, message, cat, suffix)

        return mission


    def reveal_incoming_missions(self, league, mission):
        """ VISIBILITY LAYER
        'type' : 'diplomatic|assassination'
        'success' : true|false
        'reveal' : true|false
        'data' : {}
        """

        cat = mission['type']

        # Failed Assassination Attempt
    
        # MEEREEN: ignore the hidden property on the diplomatic mission and reveal its 

        if cat is 'assassination' and mission['reveal']:
        
            # The player you attacked receives two items of Roster Intelligence from torturing your assassin.
            
            if not mission['success']:
                target_house = mission['data']['house']
                target_roster = league.get_house_player(target_house).character_health
                intelligence = {}

                intel = RosterIntelligence.generate(target_house, target_roster,
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

                target_house_name = league.get_house_player(self.name).house.full_name
                for code, i in intel.iteritems():
                    cat = 'foiled'
                    suffix, message = self.create_torture_msg(code, target_house_name, i['message'])
                    suffix = "_".join([target_house, suffix])

                    league.game.update_player_chronicles(keys, message, cat, suffix)

                # The player you attacked also receives the assassin’s Prominence and Violence Power.

                assassin = league.game.characters[mission['data']['agent']]
                a_msg = "The assassin was sent by {}, has Prominence Power {}, and Violence Power {} - They escaped... but we've sent the hounds on them...".format(
                        target_house_name, assassin.prominence, assassin.violence)

                suffix, message = self.create_torture_msg('torture_'+target_house, target_house_name, a_msg)

                league.game.update_player_chronicles(keys, message, cat, suffix)


    # SCORING

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


class HouseArryn(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Arryn'
        self.bonus = {'jockey':20}
        self.immunity = 'petyrbaelish'
        super(HouseArryn, self).__init__(**self.bonus)


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

            arryn_intel = self.conduct_diplomacy(missions, target_health, characters, players)

            keys = {
                "league" : league.name,
                "episode" : league.current_episode,
                "player" : league.get_house_player(self.name).id
            }

            intelligence = keys.copy()
            intelligence.update({"intelligence": arryn_intel, 'agent': 'Arryn Ability'})

            league.game.update_player_intelligence(keys, intelligence, append=True)
         
        return intel

class HouseBolton(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Bolton'
        self.bonus = {'damage':10,'support':10}
        super(HouseBolton, self).__init__(**self.bonus)

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

        if random.random() > v/(100/15.0):

            damage.update({
                "target_house" : league.get_player_house(missions['player']),
                "target_character" : missions['assassination_agent'],
                "damage_intended" : damages[violence],
                "damage_dealt" : damage_dealt,
                "bounty" : 0,
                "success" : True
            })

        # TODO Add Chronicle Entry

        return damage



class HouseGreyjoy(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Greyjoy'
        self.bonus = {'damage': 20}
        self.immunity = 'theongreyjoy'

        super(HouseGreyjoy, self).__init__(**self.bonus)

    def bonus_mission(self, league, missions, target_roster):
        
        # GREYJOY ABILITY

        # Theon splatter damage. On a succesful attack by Theon,
        # all characters of the other roster take $5\%$ damage
        print '>>> THEON NEEDS SPLATTER DAMAGE'



class HouseIndependent(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'Independents'
        self.immunity = 'jaqenhghar'
        self.bonus = {'style':10,'support':10}
        super(HouseIndependent, self).__init__(**self.bonus)


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

    def damage_dealt(self, agent, target_house, league):

        # MARTELL ABILITY :

        #  All attacks to become lethal, provided that the total prominence power
        #  of this House is lower than the prominence of the target's roster

        if self.roster_prominence < league.get_house_player(target_house).roster_prominence:
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
        self.immunity = 'varys'
        super(HouseMeereen, self).__init__(**self.bonus)


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


    def counter_intelligence(self, league, missions, intel, characters, players):

        # NIGHTWATCH ABILITY

        # Dissemination of misinformation. Chance of false intel to be recovered in
        # diplomatic missions run against this house is 50%

        # DEVELOPER
        # if random.random() < 1:
        if random.random() < 0.5:
            false_roster = self.generate_random_roster(characters)
            intel = self.conduct_diplomacy(missions, false_roster, characters, players)          
            
        return intel

class HouseStark(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Stark'
        self.bonus = {'support':20}
        super(HouseStark, self).__init__(**self.bonus)

    def conduct_diplomacy(self, missions, target_health, characters, players):
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

        other_players = [p for p in players if p.house.name is not self.name]
        northman_target = random.sample(other_players, 1)[0]

        target_house = northman_target.house.name
        target_roster = northman_target.character_health
        intel = RosterIntelligence.generate(target_house, target_roster,
                                    characters, self.intelligence_logs, 3)
        intelligence.update(intel)

        return intelligence


class HouseTargaryen(House):
    def __init__(self, name):
        self.name = name
        self.full_name = 'House Targaryen'
        self.bonus = {'damage':10,'jockey':10}
        super(HouseTargaryen, self).__init__(**self.bonus)


class HouseTyrell(House):
    def __init__(self, name):
        self.name = name
        self.full_name = "House Tyrell"
        self.bonus = {'style':20}
        super(HouseTyrell, self).__init__(**self.bonus)
