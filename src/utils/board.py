from dataclasses import dataclass
from enum import Enum

class TurnType(Enum):
    TAKING_CARD_IN_OPEN = 0
    TAKING_CARD_IN_CLOSE = 1
    TAKING_DESTINATION_TICKETS = 2
    BUILDING_STRETCH = 3

class GameType(Enum):
    LOCAL_GAME = 0
    BOT_GAME = 1

class DifficultyLevel(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2

class TrainChipColors(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    BLACK = 4

class Map:
    pass