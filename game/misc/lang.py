import json, os

class Lang:
    # These constants are just so I don't have to remember the keys for the json file and so I can change them easily
    MENU_ACTION_BACK          = "menu_action_back"
    MENU_ACTION_OPTIONS       = "menu_action_options"
    MENU_ACTION_PLAY          = "menu_action_play"
    MENU_ACTION_QUIT          = "menu_action_quit"
    MENU_ACTION_RESUME        = "menu_action_resume"
    MENU_ACTION_EXIT          = "menu_action_exit"
    MENU_ACTION_NEW_GAME      = "menu_action_new_game"
    MENU_ACTION_CREATE        = "menu_action_create"

    GAME_DISPLAY_TIME         = "game_display_time"
    GAME_DISPLAY_DAY          = "game_display_day"
    GAME_DISPLAY_NEW_SAVE     = "game_display_new_save"
    GAME_DISPLAY_PLAY_GAME    = "game_display_play_game"
    GAME_DISPLAY_STATE_PAUSED = "game_display_state_paused"

    TEXT_PROMPT_SAVE_NAME     = "text_prompt_save_name"


    def __init__(self):
        """
        Loads the language file from the settings.json file
        """
        with open('data/config/settings.json', 'r') as f:
            selected_language = json.load(f)['selected_language']
            if selected_language.lower() + '.json' not in os.listdir('data/config/lang'):
                print(f"Language '{selected_language}' not found! Defaulting to 'en'...")
                selected_language = 'en'
        
        with open(f'data/config/lang/{selected_language.lower()}.json', 'r') as f:
            self.lang = json.load(f)
    
    def reload(self) -> None:
        self.__init__() # probably would be better to just have load function and call the load function inside init and this
    
    def get(self, key: str) -> str:
        return self.lang[key]