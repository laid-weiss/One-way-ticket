from ..utils import game_settings
from ..utils.board import DifficultyLevel, TrainChipColors
from ..utils import constants

class SettingsModel:
    def __init__(self):
        # Game Mode
        self.mode_options = list(game_settings.GameType)
        self.game_mode = game_settings.GameType.LOCAL_GAME
        
        # Bot Difficulty 
        self.difficulty_options = list(DifficultyLevel)
        self.bot_difficulty = DifficultyLevel.EASY
        
        # Local Players
        self.player_options = [i for i in range(constants.MIN_PLAYERS, constants.MAX_PLAYERS + 1)]
        self.num_players = constants.MIN_PLAYERS
        
        # Colors 
        self.color_options = list(TrainChipColors)
        self.player_colors = list(TrainChipColors)