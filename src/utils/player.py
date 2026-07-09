from dataclasses import dataclass
from enum import Enum, auto
import train_cards
import destination_tickets
from .constants import COLORS

class PlayerType(Enum):
    BOT = 0
    LOCALPLAYER = 1
    NETWORK_HOST_PLAYER = 2
    NETWORK_CLIENT_PLAYER = 3

class PlayerStatus(Enum):
    Active = auto()
    NotActive = auto()
    # Состояния ошибок валидации хода
    ErrorInvalidAction = auto()          # Неверное действие для текущей фазы
    ErrorLocomotiveSecondCard = auto()   # Попытка взять локомотив второй картой
    ErrorTrackAlreadyTaken = auto()      # Перегон уже занят
    ErrorNotEnoughRouteCards = auto()    # Попытка сбросить все 3 карты маршрутов

class PlayerAction(Enum):
    TakeOpenCard = auto()
    TakeCloseCard = auto()
    TakeRouteCard = auto()
    ThrowRouteCard = auto()
    BuildPath = auto()

class TRAIN_CHIP_COLOR(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    BLACK = 4

@dataclass
class Player:
    ID : int
    Status : PlayerStatus
    train_deck : train_cards.PlayerTrainCardDeck
    route_deck : destination_tickets.PlayerDestinationTicketDeck
    temp_route_deck : destination_tickets.PlayerDestinationTicketDeck
    type : PlayerType
    chip_color : TRAIN_CHIP_COLOR
    remaining_train_chips : int
    points : int
