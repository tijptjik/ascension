# ROSTER HEALTH
''' HEALTH PER ROSTER CHARACTER 

'character_health':
    <league_id><house_id><episode_id> :
        "league" : <league_id>,
        "episode" : <episode_id>,
        "house" : <house_id>,
        "health" : 
            <character_id> : health
            <character_id> : health
            <character_id> : health
            <character_id> : health
            <character_id> : health
            <character_id> : health
            <character_id> : health

'''

'''
EPISODE SCORES PER CHARACTER PER AWARD

'episode_scores'
	<league_id>+<episode_id>+<award> :
		"episode" : <episode_id>,
        "award" : <award>,
        "scores" : 
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>

'''


''' PLAYER SCORES PER CHARACTER PER AWARD
'player_award_scores':
	<league_id>+<episode_id>+<award>+<player_id> :
        "episode" : <episode_id>,
        "award" : <award>,
        "player" : <player_id>,
        "scores" : 
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
        	<character_id> : <score>
'''


# 
'''PLAYER SCORES PER AWARD PER EPISODE

'player_episode_scores':
	<league_id>+<episode_id>+<player_id> :
        "episode" : <episode_id>,
        "player" : <player_id>,
        "scores" : 
        	<award> : <score>
        	<award> : <score>
        	<award> : <score>
        	<award> : <score>
        	<award> : <score>
'''


# 
''' PLAYER SCORES PER EPISODE

'leaderboard':
	<league_id><episode_id> :
		"episode" : <episode_id>,
        "scores" : 
        	<player> : <score>
        	<player> : <score>
        	<player> : <score>
        	<player> : <score>
        	<player> : <score>

'''

# 
''' INTELLIGENCE  PER PLAYER 
"player_ingelligence"
    <league_id>+<episode_id>+<player_id>:
        "league" : <league>
        "episode" : <episode_id>,
        "player" : <player_id>,
        "intelligence" :
            <intel_code> :
                "message" : <intel_msg>,
                "code" : <intel_code>,
                "type" : 'roster|character'
                "target_house" : <house_id>,
                "target_character" : <character_id>
                "source" : 'mission|ability|attempt'
'''


''' ASSASSION SCORE PER PLAYER
"player_murders"
    <league_id>+<episode_id>+<player_id>:
        "league" : <league>
        "episode" : <episode_id>,
        "player" : <player_id>,
        "murders" : 
                "target_house" : <house_id>,
                "target_character" : <character_id>,
                "damage_intended" : 100,
                "damage_dealt" : 50,
                "bounty": 120,
                "success" : true,
'''

''' CHRONICLE ENTRY SCORE PER PLAYER
"player_chronicle"
    <league_id>+<episode_id>+<player_id>:
        "league" : <league>
        "episode" : <episode_id>,
        "player" : <player_id>,
        "articles" :
            <hash> :
                "message" : <intel_msg>,
                "source" : 'mission|ability|attempt'
'''

''' CHRONICLE ENTRY SCORE PER PLAYER
"public_chronicle"
    <league_id>+<episode_id>:
        "league" : <league>
        "episode" : <episode_id>,
        "articles" :
            <hash> :
                "message" : <intel_msg>,
                "source" : 'mission|ability|attempt'
'''

""" VISIBILITY LAYER
'type' : 'diplomatic|assassination'
'success' : true|false
'reveal' : true|false
'data' : {}
"""