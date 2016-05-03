'''
INTELLIGENCE
'''
import random
from collections import Counter

class Intelligence(object):
    """Intelligence

    Example : This character has more diplomacy than prominence, but less damage than both
    """

    target_type = 'roster|character'

    def __init__(self):
        super(Intelligence, self).__init__()

    @classmethod
    def generate(cls, target_house, target_roster, characters, intelligence_logs, count=1,
         episode_number=None, refresh=False):

        
        health = target_roster.copy()

        target_roster = cls.get_roster_properties(target_roster.keys(), characters)

        for char in target_roster:
            char.health = health[char.id]

        intel = [cls._random_selector(target_house, target_roster,
                        intelligence_logs, episode_number) for _ in range(count)]
        codes = [i['code'] for i in intel]

        return dict(zip(codes,intel))

    @classmethod
    def _random_selector(cls, target_house, target_roster, intelligence_logs, episode_number=None):
        return cls.get_intel_template(cls.target_type, target_house)

    @classmethod
    def add_house_target_code(cls, prefix, target_house):
        comps = prefix.split('|')
        return "|".join([comps[0],target_house[:2].upper()] + comps[1:])

    @classmethod
    def add_char_target_code(cls, prefix, target_house, target_char):
        comps = prefix.split('|')
        prefix = "|".join([comps[0], getattr(target_char,'id')[:3].upper() + getattr(target_char,'id')[-1].upper()] + comps[1:])
        return cls.add_house_target_code(prefix, target_house)

    @staticmethod
    def get_roster_properties(target_roster, characters):
        return [characters[char] for char in target_roster]

    @staticmethod
    def get_relevant_intelligence(intelligence_logs, target_type='roster', character=None):
        codes = []
        
        if not intelligence_logs:
            return codes
        
        for intel in intelligence_logs:
            for code, i in intel['intelligence'].iteritems():
                if character and 'target_character' in i and i['target_character'] == character:
                        codes.append(code)
                elif not character and i['type'] == target_type:
                        codes.append(code)

        return codes


    @staticmethod
    def get_intel_template(target_type, target_house,target_character=None):
        intel_template = {
            "message" : "<intel_msg>",
            "code" : "<code_" + str(random.getrandbits(8)) + ">",
            "type" :     target_type,
            "target_house" : target_house,
            "target_character" : target_character
        }
        return intel_template

    @staticmethod
    def get_random_character_property():
        options = {
            'H' : 'house',
            'P' : 'prominence',
            'D' : 'diplomacy',
            'V' : 'violence',
        }
        choice = random.sample(options,1)[0]
        
        return choice, options[choice] 

    @staticmethod
    def get_random_character_power():
        options = {
            'P' : 'prominence',
            'D' : 'diplomacy',
            'V' : 'violence',
        }
        choice = random.sample(options,1)[0]
        
        return choice, options[choice]

class RosterIntelligence(Intelligence):
    """RosterIngelligence

    Example : There are more Starks than Lannisters, both at least one
    Example : The 
    """
    target_type = 'roster'
    ratings = [0, 'all the same', 'rarely different', 'a decent range', 'diverse', 'extremely varied', 'all but one unique', 'all unique']

    def __init__(self):
        super(RosterIngelligence, self).__init__()

    @classmethod
    def _random_selector(cls, target_house, target_roster, intelligence_logs, episode_number=None):

        previous_intel_codes = cls.get_relevant_intelligence(intelligence_logs, 'roster')
        new_intel = cls.get_intel_template(cls.target_type, target_house)

        while True:

            intel_types = [
                cls._on_house_prevalence,
                # TODO Activate _on_power_prevalencs
                # cls._on_power_prevalence,
                cls._on_power_sum,
                cls._on_diversity]

            new_intel['code'], new_intel['message'] = random.sample(intel_types,1)[0](target_house, target_roster)

            if not new_intel['code'] or new_intel['code'] in previous_intel_codes:
                continue
                
            else:
                # from pprint import pprint
                # pprint(new_intel)
                return new_intel

    @classmethod
    def _on_house_prevalence(cls, target_house, target_roster):
        """
        CODES:
        R|HP|{ARBO,BOGR...}
        """
        code_prefix = 'R|HP|'
        code_prefix = cls.add_house_target_code(code_prefix, target_house)

        houses = Counter([getattr(char,'house') for char in target_roster])
        if len(houses) < 2:
            code_suffix = 'XXXX'
            msg = "All characters belong to the same house".format()
            return code_prefix + code_suffix, msg
            
        select_houses = sorted(random.sample(houses.keys(),2))
        code_suffix = "".join([h[:2].upper() for h in select_houses])

        if houses[select_houses[0]] == houses[select_houses[1]]:
            msg = "There are as many {} characters as there are {} characters, both at least one".format(*[h.title() for h in select_houses])
            return code_prefix + code_suffix, msg

        if houses[select_houses[0]] > houses[select_houses[1]]:
            direction = "more"
        else:
            direction = "less"
        
        msg = "There are {} {} characters than {} characters, both at least one".format(direction, select_houses[0].title(), select_houses[1].title())
        
        return code_prefix + code_suffix, msg

    @classmethod
    def _on_power_prevalence(cls, target_house, target_roster):
        """
        CODES:
        R|PP|{P,D,V}
        """
        # TODO Still needs to be implmented
        code_prefix = 'R|PP|'
        code_prefix = cls.add_house_target_code(code_prefix, target_house)

        code_suffix, key = cls.get_random_character_power()
        msg = ''
        return code_prefix + code_suffix, msg

    @classmethod
    def _on_power_sum(cls, target_house, target_roster):
        """
        EXAMPLES:
        * The roster's total X is higher than its total Y, and its total Z is lower than X
        * The roster's total X is higher than its total Y, and its total Z is equal to one of them
        * The roster's totals for X, Y, and Z are no different from each other
        
        CODES:
        C|PS|{1,2X?,2N?,3}
        """
        code_prefix = 'C|PS|'
        code_prefix = cls.add_house_target_code(code_prefix, target_house)

        powers = ['prominence', 'diplomacy', 'violence']
        roster_powers = [sum([getattr(c, power) for c in target_roster]) for power in powers]

        cp = [p.title() for p in powers]

        # All the same
        if len(set(roster_powers)) == 1:
            msg = "The roster's totals for {}, {}, and {} are no different from each other.".format(*cp)
            code_suffix = '1'
            return code_prefix + code_suffix, msg
        
        # Shared Max
        max_list = set([i for i, x in enumerate(roster_powers) if x == max(roster_powers)])
        if len(max_list) > 1:
            max_idx = random.sample(max_list,1)
            other_max_idx = list(max_list.difference(max_idx))
            min_idx = list(set([0,1,2]).difference(max_list))
            code_suffix = '2X' + cp[max_idx[0]][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is equal to one of them.".format(cp[max_idx[0]], cp[min_idx[0]], cp[other_max_idx[0]])
        
        # Shared Min
        min_list = set([i for i, x in enumerate(roster_powers) if x == min(roster_powers)])
        if len(min_list) > 1:
            max_idx = list(set([0,1,2]).difference(min_list))
            min_idx = random.sample(min_list,1)
            other_min_idx = list(min_list.difference(min_idx))
            code_suffix = '2N' + cp[min_idx[0]][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is equal to one of them.".format(cp[max_idx[0]], cp[min_idx[0]], cp[other_min_idx[0]])
        
        # All Different
        if len(set(roster_powers)) == 3:
            max_idx = roster_powers.index(max(roster_powers))
            less_list = [0,1,2]
            del less_list[max_idx]
            less_idx = random.sample(less_list,1)[0]
            other_less_idx = list(set(less_list).difference([less_idx]))[0]
            code_suffix = '3' + cp[less_idx][0]
            msg = "The roster's total {} is higher than its total {}, and its total {} is lower than one of them.".format(cp[max_idx], cp[less_idx], cp[other_less_idx])
        
        return code_prefix + code_suffix, msg


    @classmethod
    def _on_diversity(cls, target_house, target_roster):
        """
        CODES:
        R|D|{H,P,D,V}
        """
        code_prefix = 'R|D|'
        code_prefix = cls.add_house_target_code(code_prefix, target_house)

        code_suffix, key = cls.get_random_character_property()

        prop_count = len(set([getattr(char,key) for char in target_roster]))
        rating = cls.ratings[prop_count]

        msg = "The {} traits of the roster are {}".format(key.title(),rating)

        return code_prefix + code_suffix, msg

class CharacterIntelligence(Intelligence):
    """CharacterIntelligence

    Example :
        * One Item Specifically : e.g. "Character has '5' Prominence", "Character is a Lannister", or 
        * Two items Relatively : e.g. 'The Character has higher Prominence than Violence, but Diplomacy equal to one of them', or 'Character is the only member of this House on the Roster'.
    """
    
    target_type = 'character'

    def __init__(self):
        super(RosterIngelligence, self).__init__()

    @classmethod
    def _random_selector(cls, target_house, target_roster, intelligence_logs, episode_number=None):

        target_lock = cls._get_character_lock(target_roster, intelligence_logs)
        if not target_lock:
            target_lock = cls._set_character_lock(target_roster)

        previous_intel_codes = cls.get_relevant_intelligence(intelligence_logs, 'character', character=target_lock)
        new_intel = cls.get_intel_template(cls.target_type, target_house, target_lock)

        if target_lock:
            target_lock = cls.get_roster_character(target_roster, target_lock)

        
        while True:

            intel_types = [
                cls._on_absolute_trait,
                cls._on_relative_trait,
                cls._on_extreme_trait,
                cls._on_unique_trait]
                

            new_intel['code'], new_intel['message'] = random.sample(intel_types,1)[0](target_house, target_lock, target_roster)

            if not new_intel['code'] or new_intel['code'] in previous_intel_codes:
                continue
                
            else:
                # from pprint import pprint
                # pprint(new_intel)
                
                return new_intel
    
    @classmethod
    def get_roster_character(cls, roster, character):
        try:
            # do stuff that throws an IndexError
            return [char for char in roster if char.id == character][0]
        except IndexError:
            import pdb; pdb.set_trace()

    @classmethod
    def _on_absolute_trait(cls, target_house, target_character,  target_roster):
        """
        EXAMPLES:
        * Character's X Power is N
        * Character is affiliated with House X

        CODES:
        C|A|{H,P,D,V}
        """
        code_prefix = 'C|A|'
        code_prefix = cls.add_char_target_code(code_prefix, target_house, target_character)
        code_suffix, key = cls.get_random_character_property()

        if code_suffix == 'H':
            msg = "Character is affiliated with House {}".format(getattr(target_character, key).title())
        else:
            msg = "Character's {} Power is {}".format(key.title(), getattr(target_character, key))
        
        return code_prefix + code_suffix, msg

    
    @classmethod
    def _on_relative_trait(cls, target_house, target_character,  target_roster):
        """
        EXAMPLES:
        * X is higher than Y, and Z is lower than X
        * X is higher than Y, and Z is equal to one of them'
        * X, Y, and Z are no different from each other
        
        CODES:
        C|R|{1,2X?,2N?,3}
        """
        code_prefix = 'C|R|'
        code_prefix = cls.add_char_target_code(code_prefix, target_house, target_character)

        powers = ['prominence', 'diplomacy', 'violence']
        character_powers = [getattr(target_character, power) for power in powers]
        cp = [p.title() for p in powers]

        # All the same
        if len(set(character_powers)) == 1:
            msg = "The {}, {}, and {} powers for this Character are no different from each other".format(*cp)
            code_suffix = '1'
            return code_prefix + code_suffix, msg

        # Shared Max
        max_list = set([i for i, x in enumerate(character_powers) if x == max(character_powers)])
        if len(max_list) > 1:
            max_idx = random.sample(max_list,1)
            other_max_idx = list(max_list.difference(max_idx))
            min_idx = list(set([0,1,2]).difference(max_list))
            code_suffix = '2X' + cp[max_idx[0]][0]
            msg = "{} is higher than {}, and {} is equal to one of them.".format(cp[max_idx[0]], cp[min_idx[0]], cp[other_max_idx[0]])

        # Shared Min
        min_list = set([i for i, x in enumerate(character_powers) if x == min(character_powers)])
        if len(min_list) > 1:
            max_idx = list(set([0,1,2]).difference(min_list))
            min_idx = random.sample(min_list,1)
            other_min_idx = list(min_list.difference(min_idx))
            code_suffix = '2N' + cp[min_idx[0]][0]
            msg = "{} is higher than {}, and {} is equal to one of them.".format(cp[max_idx[0]], cp[min_idx[0]], cp[other_min_idx[0]])

        # All Different
        if len(set(character_powers)) == 3:
            max_idx = character_powers.index(max(character_powers))
            less_list = [0,1,2]
            del less_list[max_idx]
            less_idx = random.sample(less_list,1)[0]
            other_less_idx = list(set(less_list).difference([less_idx]))[0]
            code_suffix = '3' + cp[less_idx][0]
            msg = "{} is higher than {}, and {} is lower than one of them.".format(cp[max_idx], cp[less_idx], cp[other_less_idx])
        
        return code_prefix + code_suffix, msg
    

    @classmethod
    def _on_extreme_trait(cls, target_house, target_character, target_roster):
        """
        EXAMPLES:
        * Character has the highest X of anyone on the target roster
        * Character has the (shared) lowest X of anyone on the target roster

        CODES:
        C|E|{X,N}|{P,D,V}
        """
        code_prefix = 'C|E|'
        code_prefix = cls.add_char_target_code(code_prefix, target_house, target_character)

        properties = ['prominence','diplomacy','violence']
        random.shuffle(properties)
        code_suffix = ''
        msg = ''

        for property in properties:
            char_prop = getattr(target_character, property)
            code_suffix = property.title()[0]

            is_max, is_shared = cls.is_property_max_on_roster(target_character, property, char_prop, target_roster)
            if is_max:
                shared = " "
                if is_shared:
                    shared = " (shared) "
                code_suffix = 'X|' + code_suffix

                msg = "Character has the{}highest {} Power on the target roster".format(shared, property.title())
                return code_prefix + code_suffix, msg

            is_min, is_shared = cls.is_property_min_on_roster(target_character, property, char_prop, target_roster)
            
            if is_min:
                shared = " "
                if is_shared:
                    shared = " (shared) "

                code_suffix = 'N|' + code_suffix
                msg = "Character has the{}lowest {} Power on the target roster".format(shared, property.title())
                return code_prefix + code_suffix, msg

        # If there are no extreme traits, fail
        return None, 'Mission Error'


    @classmethod
    def _on_unique_trait(cls, target_house, target_character, target_roster):
        """
        EXAMPLES:
        * Character is the only member of this House on the target roster
        * Character is the only one with this X Power on the target roster

        CODES:
        C|U|{H,P,D,V}
        """
        code_prefix = 'C|U|'
        code_prefix = cls.add_char_target_code(code_prefix, target_house, target_character)
        
        properties = ['house','prominence','diplomacy','violence']

        random.shuffle(properties)

        for property in properties:
            char_prop = getattr(target_character, property)
            code_suffix = property.title()[0]
            if cls.is_property_unique_on_roster(target_character, property, char_prop, target_roster):
                if property is 'house':
                    msg = "Character is the only member of this House on the target roster".format(char_prop)
                else:
                    msg = "Character is the only one with this {} Power on the target roster".format(property.title())
                return code_prefix + code_suffix, msg
            else:
                continue

        # If there are no unique traits, fail
        return None, 'Mission Error'


    @classmethod
    def _get_character_lock(cls, target_roster, intelligence_logs):

        # If there are no previous character missions:
        if not intelligence_logs:
            return None

        locks = {}

        # If there are previous character missions, select the latest target

        for intel in intelligence_logs:
            for code, i in intel['intelligence'].iteritems():
                if 'target_character' in i and i['target_character'] and target_roster == i['target_house']:
                    locks[intel['episode']] = i['target_character']

        if not locks:
            return None

        character_lock = locks[max(locks)]

        # If the character is still alive, return existing character.
        
        if getattr(cls.get_roster_character(target_roster,character_lock),'health') > 0:
            return character_lock
        
        # If they have died, release the target lock.

        else:
            return None

    @classmethod
    def is_property_unique_on_roster(cls, target_character, k, v, target_roster):
        
        for c in target_roster:
            if c is not target_character and getattr(c, k) == v:
                return False
        return True

    @classmethod
    def is_property_max_on_roster(cls, target_character, k, v, target_roster):
        for c in target_roster:
            is_shared = False
            if c is not target_character and getattr(c, k) > v:
                return False, None
            if c is not target_character and getattr(c, k) == v:
                is_shared = True
        return True, is_shared

    @classmethod
    def is_property_min_on_roster(cls, target_character, k, v, target_roster):
        for c in target_roster:
            is_shared = False
            if c is not target_character and getattr(c, k) < v:
                return False, None
            if c is not target_character and getattr(c, k) == v:
                is_shared = True
        return True, is_shared

    @staticmethod
    def _set_character_lock(target_roster):
        target_roster = [c.id for c in target_roster if c.health > 0]
        return random.sample(target_roster, 1)[0]