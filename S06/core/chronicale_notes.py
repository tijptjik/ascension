    def update_player_chronicles(self, keys, message, cat, suffix=''):
        ''' ENTRY PER PLAYER CHRONICLE 
        'player_chronicles':
        <league_id><house_id><episode_id> :
            "episode" : <episode_id>,
            "house" : <house_id,
            "entries" : 
                'diplomacy_' + code> : 
                    'msg' : <msg>
                    'type': <type>
                'assassination' : <entry>
                'ability_' + <house_id> : <entry>
                'target_' + <character_id> : <entry>
                'foiled_' + <house_id> : <entry>
                'awards_' + <award_id> : <entry>
                'ranking' : <entry>
        '''

    def update_league_chronicles(self, keys, message, cat, suffix=''):
        ''' ENTRY PER LEAGUE CHRONICLE
        'league_chronicles':
        <league_id><episode_id> :
            "episode" : <episode_id>,
            "entries" : 
                'damage' + <house_id> + <char_id> : 
                    'msg' : <msg>,
                    'type': <type>
                'death' + <house_id> + <char_id> : <entry>
        '''
