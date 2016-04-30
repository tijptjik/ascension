# ROSTER HEALTH

 '''
'character_health':
    <roster_id> :
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