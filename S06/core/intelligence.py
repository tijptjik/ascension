'''
INTELLIGENCE
'''

class Intelligence(object):
    """Intelligence

    Example : This character has more diplomacy than prominence, but less damage than both
    """
    def __init__(self):
        super(Intelligence, self).__init__()

    @classmethod
    def generate(cls, target_house, target_roster, characters, intelligence_logs, count=1,
        episode_number=None, refresh=False):

        codes = range(4)
        intel = range(4)

        print target_house, count, intelligence_logs
        print (codes, intel)

        return dict(zip(codes,intel))

    def get_roster_properties(self):
        return 

class RosterIntelligence(Intelligence):
    """RosterIngelligence

    Example : There are more Starks than Lannisters, both at least one
    """
    def __init__(self):
        super(RosterIngelligence, self).__init__()

class CharacterIntelligence(Intelligence):
    """docstring for RosterIngelligence"""
    def __init__(self):
        super(RosterIngelligence, self).__init__()

    def _on_absolute_trait(self):
        pass
    def _on_relative_trait(self):
        pass
    def _on_extreme_trait(self):
        pass
