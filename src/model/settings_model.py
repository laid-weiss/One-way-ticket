from ..utils.board import DifficultyLevel, GameType, TrainChipColors
from ..utils.game_settings import GameSettings
from ..utils import constants


class SettingsModel:
    def __init__(self, settings: GameSettings | None = None):
        # Game Mode
        self.mode_options = list(GameType)
        self.game_mode = GameType.LOCAL_GAME

        # Bot Difficulty
        self.difficulty_options = list(DifficultyLevel)
        self.bot_difficulty = DifficultyLevel.EASY

        # Local Players
        self.player_options = [i for i in range(constants.MIN_PLAYERS, constants.MAX_PLAYERS + 1)]
        self.num_players = constants.MIN_PLAYERS

        # Colors
        self.color_options = list(TrainChipColors)
        self.player_colors = list(TrainChipColors)

        if settings is not None:
            current = settings.get_settings
            self.game_mode = current.game_type
            self.num_players = current.number_of_players
            converted_colors = []
            for color in current.chip_colors:
                converted_colors.append(TrainChipColors[color.name])
            self.player_colors = converted_colors + [c for c in self.color_options if c not in converted_colors]
