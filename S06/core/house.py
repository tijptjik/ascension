from abc import ABCMeta, abstractmethod
from utils import ScoreCounter

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

    @abstractmethod
    def run_diplomatic_mission(self, missions, characters):
        pass

    def run_against_character(self, diplomacy_power):
        return diplomacy_power > 3

    def run_against_roster(self, diplomacy_power):
        return diplomacy_power < 4 

    def get_intel_count(self, diplomacy_power):
        return [0,1,2,3,1,2][diplomacy_power]

    def conduct_diplomacy(self, missions, target_roster, characters):
        d = getattr(characters[missions['diplomatic_agent']],'diplomacy')
        
        target_house = missions['diplomatic_target_house']

        intel_count = self.get_intel_count(d)

        # STARK : Assitance from the Northmen - An addition Level 3 diplomatic mission is run each episode against a random House on this House's behest
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

    def counter_intelligence(self, league, missions, intel):

        # ARRYN : Chance of recovering intel from the source of diplomatic missions run against this house - Chance is $50\%$, intel at same level as the mission

        # NIGHTWATCH : Dissemination of misinformation. Chance of false intel to be recovered in diplomatic missions run against this house is $50\%$
        intel = intel
        return intel

    @abstractmethod
    def run_assassination_mission(self):
        pass

        

    def plot_assassination(self,mission):

        # GREYJOY : Theon splatter damage. On a succesful attack by Theon, all characters of the other roster take $5\%$ damage

        # self.damage_dealt(mission)

        pass

    def foil_assassination(self,mission):
        # Chance that an attack on this House backfires and retargets the assassin itself - Chance is $15\% *$ target's prominence power

        # Check Immunity

        pass

    def damage_dealt(self, mission):
        # MARTELL : All attacks to become lethal, provided that the total prominence power of this House is lower than the prominence of the target's roster

        # if self.roster_prominence < target.roster_prominence: 
        pass

    def reveal_outgoing_missions(self, mission):

        # Mission Type and Result

        # If Diplomacy / Succesful Attack - set to hide by default

        # If Failed Attack - set to reveal by default

        # Target player target_player.house.reveal_missions_target()

        # TYRELL : don't call() target_player.house.reveal_missions_target()
        pass

    def reveal_incoming_missions(self, mission):
        pass

        # MEEREEN: ignore the hidden property on the diplomatic mission and reveal its 
            # Origin House

        # Update the personal Chronicle


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
        self.bonus = {'damage': 20}
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
