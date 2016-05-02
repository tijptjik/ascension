'''
INTELLIGENCE
'''
import random

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
                if character and i['target_character'] == character:
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
    """
    target_type = 'roster'

    def __init__(self):
        super(RosterIngelligence, self).__init__()

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

            intel_types = [cls._on_absolute_trait]
            # intel_types = [cls._on_absolute_trait,
                # cls._on_relative_trait,
                # cls._on_extreme_trait,
                # cls._on_unique_trait]

            new_intel['code'], new_intel['message'] = random.sample(intel_types,1)[0](target_lock, target_roster)

            if not new_intel['code'] or new_intel['code'] in previous_intel_codes:
                continue
            else:
                return new_intel
    
    @classmethod
    def get_roster_character(cls, roster, character):
        return [char for char in roster if char.id == character][0]

    @classmethod
    def _on_absolute_trait(cls, target_character,  target_roster):
        """
        EXAMPLES:
        * Character's X Power is N
        * Character is affiliated with House X

        CODES:
        C|A|{H,P,D,V}
        """
        code_prefix = 'C|A|'

        code_suffix, key = cls.get_random_character_property()
        if code_suffix == 'H':
            msg = "Character is affiliated with House {}".format(getattr(target_character, key).title())
        else:
            msg = "Character's {} Power is {}".format(key.title(), getattr(target_character, key))
        
        return code_prefix + code_suffix, msg

    
    @classmethod
    def _on_relative_trait(cls):
        """
        EXAMPLES:
        * X is higher than Y, and Z is lower than X
        * X is higher than Y, and Z is equal to one of them'
        * X, Y, and Z are no different from each other
        
        CODES:
        C|R|{P,D,V}
        """
        code_prefix = 'C|R|'
        pass
    

    @classmethod
    def _on_extreme_trait(cls):
        """
        EXAMPLES:
        * Character has the highest X of anyone on the target roster
        * Character has the (shared) lowest X of anyone on the target roster

        CODES:
        C|E|{X,N}|{H,P,D,V}
        """
        code_prefix = 'C|E|'
        pass
    

    @classmethod
    def _on_unique_trait(cls):
        """
        EXAMPLES:
        *

        CODES:
        C|U|{H,P,D,V}
        """
        code_prefix = 'C|U|'
        # If there are no unique traits, fail
        if True:
            return None, 'Mission Error'

        return code_prefix + code_suffix

    @classmethod
    def _get_character_lock(cls,target_roster, intelligence_logs):

        # If there are no previous character missions:
        if not intelligence_logs:
            return None

        locks = {}

        # If there are previous character missions, select the latest target

        for intel in intelligence_logs:
            for code, i in intel['intelligence'].iteritems():
                if 'target_character' in i and i['target_character']:
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

    @staticmethod
    def _set_character_lock(target_roster):
        target_roster = [c.id for c in target_roster if c.health > 0]
        return random.sample(target_roster, 1)[0]