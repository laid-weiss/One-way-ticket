from .board import GameType
from .player import TRAIN_CHIP_COLOR
from dataclasses import dataclass

@dataclass
class Settings:
    game_type : GameType
    number_of_players : int
    chip_colors : list[TRAIN_CHIP_COLOR]

class GameSettings:
    __settings : Settings


    def __init__(self):
        self.__settings = Settings(GameType.LOCAL_GAME, 2, [TRAIN_CHIP_COLOR.RED, TRAIN_CHIP_COLOR.BLACK])

    def update_settings(self, gt : GameType, np : int, cc : list[TRAIN_CHIP_COLOR]) -> None:
        self.game_type = gt
        self.number_of_players = np
        self.chip_colors = cc

    @property
    def get_settings(self):
        return self.__settings