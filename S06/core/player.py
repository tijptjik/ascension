from house import *

'''
PLAYERS
'''

class Player(object):
    """A League Player"""
    def __init__(self, league, id, alias, alias_short, email, facebook, first_name, full_name,
                    roster_id=None, house=None, missions=None, votes=None):
        super(Player, self).__init__()
        self.id = id
        self.league = league
        self.alias = alias
        self.alias_short = alias_short
        self.email = email
        self.facebook = facebook
        self.first_name = first_name
        self.full_name = full_name
        self.roster_id = roster_id

        self.house = self.ofHouse(house)
        self.house.intelligence_logs = self.collect_intelligence()
        
        self.missions = self.collect_missions()
        self.votes = self.collect_votes()

    def __repr__(self):
        return '<{} @ {}>'.format(self.first_name, self.house.name.upper())

    def ofHouse(self, house):
        house_map = {
            "arryn" : HouseArryn,
            "bolton" : HouseBolton,
            "greyjoy" : HouseGreyjoy,
            "independent" : HouseIndependent,
            "lannister" : HouseLannister,
            "martell" : HouseMartell,
            "meereen" : HouseMeereen,
            "minor"   : HouseMinor,
            "nightswatch" : HouseNightswatch,
            "stark" : HouseStark,
            "targaryen" : HouseTargaryen,
            "tyrell" : HouseTyrell,
        }

        return house_map[house](house)

    def collect_votes(self):
        return filter(lambda v: v['player'] == self.id, self.league.votes)

    def collect_missions(self):
        return filter(lambda m: m['player'] == self.id, self.league.missions)

    def collect_intelligence(self):
        return filter(lambda i: i['player'] == self.id, self.league.intelligence)

    def get_roster_prominence(self, characters):
        prominence = sum([getattr(characters[character],'prominence') for character in self.roster])
        return prominence     