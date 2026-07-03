from dataclasses import dataclass
from enum import Enum

class TurnType(Enum):
    TAKING_CARD_IN_OPEN = 0
    TAKING_CARD_IN_CLOSE = 1
    TAKING_DESTINATION_TICKETS = 2
    BUILDING_STRETCH = 3

