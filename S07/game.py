import pandas as pd

episode = 7

episodes = {
    1 : 'Dragonstone',
    2 : 'Stormborn',
    3 : 'The Queen\'s Justice',
    4 : 'The Spoils of War',
    5 : 'Eastwatch',
    6 : 'Beyond the Wall',
    7 : 'The Dragon and the Wolf'
}

episode_deaths = {
    1 : [],
    2 : ['Nymeria Sand'],
    3 : ['Olenna Tyrell',],
    4 : ['Tyene Sand'],
    5 : ['Randyll Tarly','Dickon Tarly'],
    6 : ['Thoros of Myr','Benjen Stark'],
    7 : ['Petyr Baelish','Beric Dondarrion','Tormund Giantsbane'],
}

off_the_show = ['Ellaria Sand','Meera Reed','Melisandre','Robin Arryn']

booster_rounds = {
    1 : {
        "prompt" : "Who will sit on the Iron Throne?",
        "points_correct" : 50,
        "points_wrong" : 50,
        "multiple_choice" : False,
        "outcome" : 'Cercei Lannister'
    },
    2 : {
        "prompt" : "Who does Arya kill from her list?",
        "points_correct" : 25,
        "points_wrong" : 10,
        "multiple_choice" : True,
        "outcome" : ['None']
    },
    3 : {
        "prompt" : "How many dragons will perish?",
        "points_correct" : 40,
        "points_wrong" : 25,
        "multiple_choice" : False,
        "outcome" : 1
    },
    4 : {
        "prompt" : "How far south do the Whitewalkers get?",
        "points_correct" : 40,
        "points_wrong" : 25,
        "multiple_choice" : False,
        "outcome" : 'Eastwatch'
    },
    5 : {
        "prompt" : "Who won't return from beyond the wall?",
        "points_correct" : 25,
        "points_wrong" : 10,
        "multiple_choice" : True,
        "outcome" : ['Thoros of Myr']
    },
    6 : {
        "prompt" : "Who will betray their allegiance?",
        "points_correct" : 40,
        "points_wrong" : 10,
        "multiple_choice" : True,
        "outcome" : ['Jaime Lannister']

    }
}

player_abbr = {'al' : 'al', 
    'Darth KaasThorR' : 'DKTR', 
    'de deciduous defeater' : 'ddd', 
    'Duke Popo TunaSlayer' : 'DPTS', 
    'expt_control' : 'ec', 
    'Haeleypuff' : 'Hp', 
    'Hagrid ' : 'H', 
    'House Wailixe' : 'HW', 
    'Ivarius Ironsight' : 'II', 
    'Kirsty of Wooden Spoon' : 'KoWP', 
    'Lady Signor' : 'LS', 
    'Margarine Tyrell' : 'MT', 
    'Nevel Knife' : 'NK', 
    'No Name' : 'NN', 
    'No one' : 'N1', 
    'Overqueen Sherin' : 'OqS', 
    'Pingface' : 'Pf', 
    'Septa Palindrome' : 'SPd', 
    'Ser Certainly Cersie' : 'SSC', 
    'Ser Clau' : 'SCl', 
    'Ser Cookden' : 'SCo', 
    'Ser Friendzone' : 'SFz', 
    'Ser Noser' : 'SNs', 
    'Ser Perfluous' : 'SPf', 
    'Ser Plus' : 'SP', 
    'Ser Spoon' : 'SS', 
    'Ser Teyn Deth' : 'STD', 
    'Tailwag Furdragon' : 'TFd', 
    'The Bastard Baratheon' : 'TBB', 
    'The Ochre Otter' : 'TOO', 
    'Yanneqi Silverscale' : 'YS', 
    'Zal Drogo' : 'ZD', 
    'Zen Medica' : 'ZM', 
    'δράκ0tʃɪk' : 'δt'
    }


from collections import defaultdict
import operator

rosters = pd.read_csv('rosters_clean.csv', index_col=0)
points = pd.read_csv('character_points.csv', index_col=0, usecols=[0,2,3], skiprows=1, names=['character','dead', 'alive'])

rosters = rosters.drop([ch for ch in rosters.columns if ch not in points.index] ,axis=1)

def shorten_names(df):
    df.index = pd.Series(df.index).replace({
     'Overqueen Sherin of the Glades Green' : 'Overqueen Sherin',
     'Kirsty of House Wooden Spoon' : 'Kirsty of Wooden Spoon',
     'ZB' : 'Zal Drogo'
    })
    return df

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
