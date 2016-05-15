'''
INTELLIGENCE
'''
import random
from random import choice
from collections import Counter
from pprint import pprint
from house import *

class Intelligence(object):
    """Intelligence

    Example : This character has more diplomacy than prominence, but less damage than both
    """

    def __init__(self, target_house, target_roster, chars, logs, count=1):
        super(Intelligence, self).__init__()
        
        self.count = count
        self.logs = logs

        self.intelligence_events = self.collect_intelligence_events()

        characters = self.get_roster_properties(target_roster.keys(), chars)

        for char in characters:
            char.health = target_roster[char.id]

        self.target_type = None
        self.target_house_id = target_house
        self.target_roster_characters = characters
        self.target_character_id = None
        self.target_character = None

        self.intel_types = None

        
    def generate(self):
        """{
        u'C|IN|JAQR|E|X|V': {
            u'code': u'C|IN|JAQR|E|X|V',
            u'message': u'This character has the (shared) highest <span class="power">Violence</span> Power on the target roster',
            u'target_character': u'jaqenhghar',
            u'target_house': u'independent',
            u'type': u'character'},
        u'C|IN|VARS|R|1': {
            u'code': u'C|IN|VARS|R|1',
            u'message': u'The Prominence, Diplomacy, and Violence powers for this character are no different from each other',
            u'target_character': u'varys',
            u'target_house': u'independent',
            u'type': u'character'}}
        """
        intel = [self._random_selector() for _ in range(self.count)]
        codes = [i['code'] for i in intel]

        return dict(zip(codes, intel))


    def collect_intelligence_events(self):
        """[{
        u'agent': u'branstark',
        u'episode': 51,
        u'intelligence': {
            u'C|IN|JAQR|E|X|V': {
                u'code': u'C|IN|JAQR|E|X|V',
                ... See self.generate()
        u'league': u'westeros',
        u'player': u'facebook:10153503420116080'}]
        """
        get_events = lambda e: e['intelligence'].values()
        return [event for episode in self.logs for event in get_events(episode)]

    def _random_selector(self):
        return self.get_intel_template()

    def get_target_house_code(self):
        return self.target_house_id[:2].upper()

    def add_house_target_code(self, prefix):
        comps = prefix.split('|')
        return "|".join([comps[0], self.get_target_house_code()] + comps[1:])

    def get_roster_properties(self, target_roster_character_ids, characters):
        return [characters[id] for id in target_roster_character_ids]
    
    def get_property_of_all_roster(self, prop):
        return [getattr(c, prop) for c in self.target_roster_characters]

    def get_relevant_intelligence(self):
        raise NotImplementedError
        
    def get_intel_template(self):
        intel_template = {
            "message" : "<intel_msg>",
            "code" : "<code>",
            "type" :     self.target_type,
            "target_house" : self.target_house_id,
            "target_character" : self.target_character_id
        }
        return intel_template

    def get_random_character_property(self):
        options = [
            ('H' , 'house'),
            ('P' , 'prominence'),
            ('D' , 'diplomacy'),
            ('V' , 'violence')
        ]
        return random.choice(options)

    def get_random_character_power(self):
        options = [
            ('P' , 'prominence'),
            ('D' , 'diplomacy'),
            ('V' , 'violence')
        ]
        return random.choice(options)


class RosterIntelligence(Intelligence):
    """RosterIngelligence

    Example : There are more Starks than Lannisters, both at least one
    """

    def __init__(self, *args, **kwargs):
        super(RosterIntelligence, self).__init__(*args, **kwargs)
        self.target_type = 'roster'
        
        self.ratings = [0, 'all the same', 'rarely different',
            'a decent range', 'diverse', 'extremely varied',
            'all but one unique', 'all unique']

        self.intel_types = [
            self._on_house_prevalence,
            # TODO Activate _on_power_prevalencs
            # self._on_power_prevalence,
            self._on_power_sum,
            self._on_diversity
        ]
   
    def get_relevant_intelligence(self):
        return [e['code'] for e in self.intelligence_events if
                    e['type'] == self.target_type]

    def _random_selector(self):

        intel = self.get_intel_template()

        while True:

            intel['code'], intel['message'] = random.choice(self.intel_types)()

            if not intel['code'] or intel['code'] in self.get_relevant_intelligence():
                continue
                
            self.intelligence_events.append(intel)

            return intel

    def _on_house_prevalence(self):
        """
        CODES:
        R|HP|{ARBO,BOGR...}
        """
        code_prefix = 'R|HP|'
        code_prefix = self.add_house_target_code(code_prefix)

        houses = Counter([getattr(char,'house') for char in self.target_roster_characters])
        
        if len(houses) < 2:
            code_suffix = 'XXXX'
            msg = "All characters belong to the same house".format()
            return (code_prefix + code_suffix, msg)
            
        select_houses = sorted(random.sample(houses.keys(),2))
        code_suffix = "".join([h[:2].upper() for h in select_houses])

        if houses[select_houses[0]] == houses[select_houses[1]]:
            msg = "There are as many {} characters as there are {} characters, both at least one".format(*[h.title() for h in select_houses])
            return (code_prefix + code_suffix, msg)

        if houses[select_houses[0]] > houses[select_houses[1]]:
            direction = "more"
        else:
            direction = "less"
        
        msg = "There are {} {} characters than {} characters, both at least one".format(direction, select_houses[0].title(), select_houses[1].title())
        
        return (code_prefix + code_suffix, msg)


    def _on_power_prevalence(self):
        """
        CODES:
        R|PP|{P,D,V}
        """
        # TODO Still needs to be implmented
        code_prefix = 'R|PP|'
        code_prefix = self.add_house_target_code(code_prefix)

        code_suffix, key = self.get_random_character_power()
        msg = ''
        return (code_prefix + code_suffix, msg)


    def _on_power_sum(self):
        """
        EXAMPLES:
        * The roster's total X is higher than its total Y, and its total Z is lower than X
        * The roster's total X is higher than its total Y, and its total Z is equal to one of them
        * The roster's totals for X, Y, and Z are no different from each other
        
        CODES:
        C|PS|{1,2X?,2N?,3}
        """
        code_prefix = 'C|PS|'
        code_prefix = self.add_house_target_code(code_prefix)

        powers = ['prominence', 'diplomacy', 'violence']

        roster_powers = [sum(self.get_property_of_all_roster(power)) for power in powers]

        cp = [p.title() for p in powers]

        # All the same
        if len(set(roster_powers)) == 1:
            msg = "The roster's totals for {}, {}, and {} are no different from each other.".format(*cp)
            code_suffix = '1'
            return (code_prefix + code_suffix, msg)
        
        # Shared Max
        max_list = set([i for i, x in enumerate(roster_powers) if x == max(roster_powers)])
        if len(max_list) > 1:
            max_idx = random.choice(max_list)
            other_max_idx = list(max_list.difference([max_idx]))
            min_idx = list(set([0,1,2]).difference([max_list]))
            code_suffix = '2X' + cp[max_idx][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is equal to one of them.".format(cp[max_idx], cp[min_idx[0]], cp[other_max_idx[0]])
        
        # Shared Min
        min_list = set([i for i, x in enumerate(roster_powers) if x == min(roster_powers)])
        if len(min_list) > 1:
            max_idx = list(set([0,1,2]).difference(min_list))
            min_idx = random.choice(list(min_list))
            other_min_idx = list(min_list.difference([min_idx]))
            code_suffix = '2N' + cp[min_idx][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is equal to one of them.".format(cp[max_idx[0]], cp[min_idx[0]], cp[other_min_idx[0]])
        
        # All Different
        if len(set(roster_powers)) == 3:
            max_idx = roster_powers.index(max(roster_powers))
            less_list = [0,1,2]
            del less_list[max_idx]
            less_idx = random.choice(less_list)
            other_less_idx = list(set(less_list).difference([less_idx]))[0]
            code_suffix = '3' + cp[less_idx][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is lower than one of them.".format(cp[max_idx], cp[less_idx], cp[other_less_idx])
        
        return (code_prefix + code_suffix, msg)


    def _on_diversity(self):
        """
        CODES:
        R|D|{H,P,D,V}
        """
        code_prefix = 'R|D|'
        code_prefix = self.add_house_target_code(code_prefix)

        code_suffix, key = self.get_random_character_property()

        prop_count = len(set(self.get_property_of_all_roster(key)))
        rating = self.ratings[prop_count]

        msg = "The <span class=\"power\">{}</span> traits of the roster are <span class=\"rating\">{}</span>".format(key.title(),rating)

        return (code_prefix + code_suffix, msg)


class CharacterIntelligence(Intelligence):
    """CharacterIntelligence

    Example :
        * One Item Specifically : e.g. "Character has '5' Prominence", "Character is a Lannister", or 
        * Two items Relatively : e.g. 'The Character has higher Prominence than Violence, but Diplomacy equal to one of them', or 'Character is the only member of this House on the Roster'.
    """

    def __init__(self, *args, **kwargs):
        super(CharacterIntelligence, self).__init__(*args, **kwargs)
        
        self.target_type = 'character'
        
        self.intel_types = [
            self._on_absolute_trait,
            self._on_relative_trait,
            self._on_extreme_trait,
            self._on_unique_trait
        ]

    def get_relevant_intelligence(self):
        return [e['code'] for e in self.intelligence_events if
                    e['type'] == self.target_type and
                    e['target_character'] == self.target_character_id]

    def _random_selector(self):

        self.set_target_character_lock()
        
        intel = self.get_intel_template()

        while True:

            intel['code'], intel['message'] = random.choice(self.intel_types)()

            if not intel['code'] or intel['code'] in self.get_relevant_intelligence():
                continue
                
            self.intelligence_events.append(intel)

            return intel
                
    def get_target_character_code(self):
        char = self.target_character_id
        return char[:3].upper() + char[-1].upper()

    def add_target_character_code(self, prefix):
        comps = prefix.split('|')
        prefix = "|".join([comps[0], self.get_target_character_code()] + comps[1:])
        return self.add_house_target_code(prefix)


    def _on_absolute_trait(self):
        """
        EXAMPLES:
        * Character's X Power is N
        * Character is affiliated with House X

        CODES:
        C|A|{H,P,D,V}
        """
        code_prefix = 'C|A|'
        code_prefix = self.add_target_character_code(code_prefix)
        code_suffix, key = self.get_random_character_property()

        if code_suffix == 'H':
            msg = "This character is affiliated with House <span class=\"house\">{}</span>".format(
                getattr(self.target_character, key).title())
        else:
            msg = "This character's <span class=\"power\">{}</span> Power is <span class=\"value\">{}</span>".format(
                key.title(), getattr(self.target_character, key))
        
        return (code_prefix + code_suffix, msg)

    
    def _on_relative_trait(self):
        """
        EXAMPLES:
        * X is higher than Y, and Z is lower than X
        * X is higher than Y, and Z is equal to one of them'
        * X, Y, and Z are no different from each other
        
        CODES:
        C|R|{1,2X?,2N?,3}
        """
        code_prefix = 'C|R|'
        code_prefix = self.add_target_character_code(code_prefix)

        powers = ['prominence', 'diplomacy', 'violence']

        character_powers = [getattr(self.target_character, power) for power in powers]
        cp = [p.title() for p in powers]

        # All the same
        if len(set(character_powers)) == 1:
            msg = "The {}, {}, and {} powers for this character are no different from each other".format(*cp)
            code_suffix = '1'
            return (code_prefix + code_suffix, msg)

        # Shared Max
        max_list = set([i for i, x in enumerate(character_powers) if x == max(character_powers)])
        if len(max_list) > 1:
            max_idx = random.choice(list(max_list))
            other_max_idx = list(max_list.difference([max_idx]))
            min_idx = list(set([0,1,2]).difference(list(max_list)))
            code_suffix = '2X' + cp[max_idx][0]
            msg = "For this character, <span class=\"power\">{}</span> is higher than <span class=\"power\">{}</span> , and <span class=\"power\">{}</span>  is equal to one of them.".format(cp[max_idx], cp[min_idx[0]], cp[other_max_idx[0]])

        # Shared Min
        min_list = set([i for i, x in enumerate(character_powers) if x == min(character_powers)])
        if len(min_list) > 1:
            max_idx = list(set([0,1,2]).difference(min_list))
            min_idx = random.choice(list(min_list))
            other_min_idx = list(min_list.difference([min_idx]))
            code_suffix = '2N' + cp[min_idx][0]
            msg = "For this character, <span class=\"power\">{}</span> is higher than <span class=\"power\">{}</span>, and <span class=\"power\">{}</span> is equal to one of them.".format(cp[max_idx[0]], cp[min_idx], cp[other_min_idx[0]])

        # All Different
        if len(set(character_powers)) == 3:
            max_idx = character_powers.index(max(character_powers))
            less_list = [0,1,2]
            del less_list[max_idx]
            less_idx = random.choice(less_list)
            other_less_idx = list(set(less_list).difference([less_idx]))[0]
            code_suffix = '3' + cp[less_idx][0]
            msg = "For this character, <span class=\"power\">{}</span> is higher than <span class=\"power\">{}</span>, and <span class=\"power\">{}</span> is lower than one of them.".format(cp[max_idx], cp[less_idx], cp[other_less_idx])
        
        return (code_prefix + code_suffix, msg)
    

    def _on_extreme_trait(self):
        """
        EXAMPLES:
        * Character has the highest X of anyone on the target roster
        * Character has the (shared) lowest X of anyone on the target roster

        CODES:
        C|E|{X,N}|{P,D,V}
        """
        code_prefix = 'C|E|'
        code_prefix = self.add_target_character_code(code_prefix)

        properties = ['prominence','diplomacy','violence']
        
        random.shuffle(properties)
        code_suffix = ''
        msg = ''

        for property in properties:
            char_prop = getattr(self.target_character, property)
            code_suffix = property.title()[0]

            is_max, is_shared = self.is_property_max_on_roster(property, char_prop)
            if is_max:
                shared = " "
                if is_shared:
                    shared = " (shared) "
                code_suffix = 'X|' + code_suffix

                msg = "This character has the{}highest <span class=\"power\">{}</span> Power on the target roster".format(shared, property.title())
                return (code_prefix + code_suffix, msg)

            is_min, is_shared = self.is_property_min_on_roster(property, char_prop)
            
            if is_min:
                shared = " "
                if is_shared:
                    shared = " (shared) "

                code_suffix = 'N|' + code_suffix
                msg = "This character has the{}lowest <span class=\"power\">{}</span> Power on the target roster".format(shared, property.title())
                return (code_prefix + code_suffix, msg)

        # If there are no extreme traits, fail
        return None, 'Mission Error'


    def _on_unique_trait(self):
        """
        EXAMPLES:
        * Character is the only member of this House on the target roster
        * Character is the only one with this X Power on the target roster

        CODES:
        C|U|{H,P,D,V}
        """
        code_prefix = 'C|U|'
        code_prefix = self.add_target_character_code(code_prefix)
        
        properties = ['house','prominence','diplomacy','violence']

        random.shuffle(properties)

        for property in properties:
            char_prop = getattr(self.target_character, property)
            code_suffix = property.title()[0]
            if self.is_property_unique_on_roster(property, char_prop):
                if property == 'house':
                    msg = "This character is the only member of this House on the target roster".format(char_prop)
                else:
                    msg = "This character is the only one with this <span class=\"power\">{}</span> Power on the target roster".format(property.title())
                return (code_prefix + code_suffix, msg)
            else:
                continue

        # If there are no unique traits, fail
        return None, 'Mission Error'


    def set_target_character_lock(self):

        # If there are no previous character missions:
        if not self.logs:
            self.target_character_id = self.select_target_character()

        
        # If there are previous character missions, select the latest target, if still alive
        elif not self.target_character_id:
            
            locks = {}

            for episode in self.logs:
                for code, i in episode['intelligence'].iteritems():
                    if 'target_character' in i and i['target_character'] and i['target_house'] == self.target_house_id:
                        locks[episode['episode']] = i['target_character']

            # If user has targetted a different house this round
            if not locks:
                self.target_character_id = self.select_target_character()

            # Targetting same house
            else:
                prev_target = locks[max(locks)]

                if self.is_not_immune(prev_target) and next((getattr(char, 'health') for char in self.target_roster_characters if char.id == prev_target)) > 0:
                    # If the character is still alive, return existing character.
                    self.target_character_id = prev_target
                else:
                    # If they have died, reset the target lock.
                    # TODO Send Notification that this character has since died - GHI #20
                    self.target_character_id = self.select_target_character()
            

        # If another character has already been locked onto in this round 
        else:
            pass

        self.target_character = next((char for char in self.target_roster_characters if char.id == self.target_character_id))


    def is_property_unique_on_roster(self, k, v):
        for c in self.target_roster_characters:
            if c != self.target_character and getattr(c, k) == v:
                return False
        return True

    def is_property_max_on_roster(self, k, v):
        for c in self.target_roster_characters:
            is_shared = False
            if c != self.target_character and getattr(c, k) > v:
                return False, None
            if c != self.target_character and getattr(c, k) == v:
                is_shared = True
        return True, is_shared

    def is_property_min_on_roster(self, k, v):
        for c in self.target_roster_characters:
            is_shared = False
            if c != self.target_character and getattr(c, k) < v:
                return False, None
            if c != self.target_character and getattr(c, k) == v:
                is_shared = True
        return True, is_shared

    def is_not_immune(self, character):
        # TODO Refector this into House
        immunity_map = {
            "arryn" : "petyrbaelish",
            "meereen" : "varys",
            "greyjoy" : "theongreyjoy",
            "independent" : "jaqenhghar"
        }
        return immunity_map[self.target_house] != character

    def select_target_character(self):
        target_roster_ids = [c.id for c in self.target_roster_characters
                                if c.health > 0 and self.is_not_immune(c.id)]
        
        return random.choice(target_roster_ids)