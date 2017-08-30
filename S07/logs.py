episode = 4

episodes = {
    1 : 'Dragonstone',
    2 : 'Stormborn',
    3 : 'The Queen\'s Justice',
    4 : 'The Spoils of War',
    5 : '',
    6 : '',
    7 : ''
}

episode_deaths = {
    1 : [],
    2 : ['Nymeria Sand'],
    3 : ['Olenna Tyrell'],
    4 : [],
    5 : [],
    6 : [],
    7 : [],
}


from collections import defaultdict
import operator

rosters = pd.read_csv('rosters_clean.csv', index_col=0)
points = pd.read_csv('character_points.csv', index_col=0, usecols=[0,2,3], skiprows=1, names=['character','dead', 'alive'])

rosters = rosters.drop([ch for ch in rosters.columns if ch not in points.index] ,axis=1)

def shorten_names(df):
    df.index = pd.Series(df.index).replace({
     'Overqueen Sherin of the Glades Green' : 'Overqueen Sherin',
     'Kirsty of House Wooden Spoon' : 'Kirsty of Wooden Spoon'
})

shorten_names(rosters)

currently_dead = [character for ep, deaths in episode_deaths.items() for character in deaths if ep <= episode]
points_awarded = points.apply(lambda x: x.dead if x.name in currently_dead else x.alive , axis=1)
point_increase = points.dead + abs(points.alive)

def assign_points(row):
    row[row==1] = points_awarded[row.name]
    return row

gains = defaultdict(int)
for character in episode_deaths[episode]:
    for player in rosters[character][rosters[character] != 0].index:
        gains[player] += points_awarded[character]
