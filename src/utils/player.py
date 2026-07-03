from dataclasses import dataclass
from enum import Enum
import train_cards
import destination_tickets

class PlayerType(Enum):
    BOT = 0
    LOCALPLAYER = 1
    NETWORK_HOST_PLAYER = 2
    NETWORK_CLIENT_PLAYER = 3


@dataclass
class Player:
    train_deck : train_cards.PlayerTrainCardDeck
    route_deck : destination_tickets.PlayerDestinationTicketDeck
    train_chips : int
    points : int
