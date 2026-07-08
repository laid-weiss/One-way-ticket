from dataclasses import dataclass
from enum import Enum
from . import train_cards
from . import destination_tickets
from .constants import COLORS

class PlayerType(Enum):
    BOT = 0
    LOCALPLAYER = 1
    NETWORK_HOST_PLAYER = 2
    NETWORK_CLIENT_PLAYER = 3


class TRAIN_CHIP_COLOR(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    BLACK = 4

@dataclass
class Player:
    train_deck : train_cards.PlayerTrainCardDeck
    route_deck : destination_tickets.PlayerDestinationTicketDeck
    type : PlayerType
    chip_color : TRAIN_CHIP_COLOR
    remaining_train_chips : int
    points : int
