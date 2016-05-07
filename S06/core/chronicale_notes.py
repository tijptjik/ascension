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


Personal :
1. diplomacy | Agent : Result of Diplomatic Missions 
"""
code: "C|NI|MARI|E|N|P"
 message:  "Character has the lowest Prominence Power on th..."
 target_character: "marei"
 target_house:  "nightswatch"
 type:  "character"
"""

- [x] diplomacy | Agent : Result of Diplomatic Missions 
    * Always revealed to house which sent them
        * May contain false information HOUSE NIGHTWATCH Ability, mark as `ability`
        * May have been triggered by HOUSE STARK Ability, mark as `ability`
    * HOUSE MEEREEN Ability to reveal that they were run, mark as `ability`
- [x] assassination | Agent : Result of Assassination Missions
    * Character X lost Y Health, Z remains. 
- [ ] ability | Ability : Result of Ability
    - [x] HOUSE ARRYN - Chance of recovering intel from the source of diplomatic missions run against this house - Chance is 50%, intel at same level as the mission
    - [x] HOUSE MEREEN - Knowledge of all diplomatic missions against this House
    - [0] HOUSE GREYJOY - Theon splatter damage. On a succesful attack by Theon, all characters of the other roster take 5% damage
    - [0] HOUSE MARTELL - All attacks to become lethal, provided that the total prominence power of this House is lower than the prominence of the target’s roster
    - [L] HOUSE INDEPENDENTS - The faceless man the ability to take on other personas. If Jaqen kills a Character, they join this House’s Roster
    - [0] HOUSE NIGHTSWATCH - Dissemination of misinformation. Chance of false intel to be recovered in diplomatic missions run against this house is 50%50%
    - [0] HOUSE TARGARYAN - All Characters on this House’s Roster gain 5% Bonus on a succesful attack by a Dothraki Character
    - [0] HOUSE TYRELL - Full Secrecy. Missions are never revealed. Not even to the Council of Mereen
    - [-] HOUSE STARK - Assitance from the Northmen - An addition Level 3 diplomatic mission is run each episode against a random House on this House’s behest
- [x] target | Target : Result of Health loss
    * Character X lost Y Health, Z remains.    
- [x] foiled
    * May be a message about the assassin
    * May be a diplomatic msg, awarded for a failed attempt on the roster
    * Foiled attempts by House Tyrell are not revealed. 

- [x] awards : X points in the <award> category
- [x] ranking : With X points, after Z Episodes, you rank Nth in the Y League 

Global

- [ ] failed :
- [ ] damage : 
- [ ] death : 


* Make sure Jaqen and other immunes are immune from torture 
x Chronicle : Fix the foiled being the target house not the instigator
x Chronicle : Fix award being the actual table of result in the
x Chronicle : Fix the updates overriding the higher level attributes,