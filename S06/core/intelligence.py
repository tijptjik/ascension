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

        intel = [cls._random_selector(target_house, target_roster, characters,
                        intelligence_logs, episode_number) for _ in range(count)]
        codes = [i['code'] for i in intel]

        print target_house, count, intelligence_logs
        print (codes, intel)

        return dict(zip(codes,intel))

    @classmethod
    def _random_selector(cls, target_house, target_roster, characters, intelligence_logs, episode_number=None):
        return cls.get_intel_template(cls.target_type, target_house)

    @staticmethod
    def get_roster_properties():
        return False 

    @staticmethod
    def get_intel_template(target_type, target_house):
        intel_template = {
            "message" : "<intel_msg>",
            "code" : "<code_" + str(random.getrandbits(8) + ">"),
            "type" :     target_type,
            "target_house" : target_house,
            "target_character" : None
        }
        return intel_template

class RosterIntelligence(Intelligence):
    """RosterIngelligence

    Example : There are more Starks than Lannisters, both at least one
    """
    target_type = 'roster'

    def __init__(self):
        super(RosterIngelligence, self).__init__()

class CharacterIntelligence(Intelligence):
    """docstring for RosterIngelligence"""
    
    target_type = 'character'

    def __init__(self):
        super(RosterIngelligence, self).__init__()

    def _on_absolute_trait(self):
        pass
    def _on_relative_trait(self):
        pass
    def _on_extreme_trait(self):
        pass
