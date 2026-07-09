from dataclasses import dataclass
from enum import Enum
from . import train_cards
from .destination_tickets import Destination

class TurnType(Enum):
    TAKING_CARD_IN_OPEN = 0
    TAKING_CARD_IN_CLOSE = 1
    TAKING_DESTINATION_TICKETS = 2
    BUILDING_STRETCH = 3


@dataclass
class TrackSection:
    number_of_cards : tuple[int]
    type_of_cards : tuple[train_cards.TrainCardType]
    station1 : Destination
    station2 : Destination
    owner : list[int]

# type TrackSectionsMap = list[dict[train_cards.TrainCardType, TrackSection]]


@dataclass
class Map:
    pass