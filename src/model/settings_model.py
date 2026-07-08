class SettingsModel:
    def __init__(self):
        # Game Mode
        self.mode_options = ["Local", "Bot"]
        self.game_mode = "Local" 
        
        # Bot Difficulty 
        self.difficulty_options = ["Easy", "Medium", "Hard"]
        self.bot_difficulty = "Easy"
        
        # Local Players
        self.player_options = [2, 3, 4]
        self.num_players = 2
        
        # Colors 
        self.color_options = ["Red", "Blue", "Green", "Yellow", "Black"]
        self.player_colors = {
            "P1": "Red",
            "P2": "Blue",
            "P3": "Green",
            "P4": "Yellow"
        }