from dataclasses import dataclass, field

# Импортируем твои существующие классы
from .board import TrackSectionsMap
from .train_cards import MainTrainCardDeck
from .destination_tickets import MainDestinationTicketDeck

@dataclass
class GeneralGameData:
    """
    Главный датакласс, объединяющий все игровые компоненты.
    Инициализирует дефолтные значения для каждого поля.
    """
    board: TrackSectionsMap = field(default_factory=TrackSectionsMap)
    train_cards_deck: MainTrainCardDeck = field(default_factory=MainTrainCardDeck)
    destination_tickets_dec: MainDestinationTicketDeck = field(default_factory=MainDestinationTicketDeck)