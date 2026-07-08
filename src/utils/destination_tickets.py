from dataclasses import dataclass
from enum import Enum
from . import constants
import random

class DestinationTicketType(Enum):
    LONG = 0
    SHORT = 1

#TODO add proper destinations when finalized
 
class Destination(Enum):
    LA = 0
    DC = 1
    WA = 2

@dataclass
class DestinationTicket:
    type : DestinationTicketType
    start : Destination
    finish : Destination
    price : int

#TODO add proper tickets when finalized

ALL_DESTINATION_TICKETS = [
    DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.DC, 10),
    DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.WA, 5)
]

type PlayerDestinationTicketDeck = list[DestinationTicket]

class MainDestinationTicketDeck:
    __remaining_destinations : list[DestinationTicket]
    __discard_pile : list[DestinationTicket]

    def __init__(self):
        self.__remaining_destinations = ALL_DESTINATION_TICKETS
        self.__discard_pile = []

    def draw_tickets(self)->list[DestinationTicket]:
        result = []
        if (len(self.__remaining_destinations) < 3):
            self.return_discarded_cards_to_main_deck()
        for i in range(constants.DRAW_DESTINATION_TICKETS):
            if(not self.is_empty()):
                result.append(self.__remaining_destinations.pop())
        return result

    def return_tickets(self, *tickets) -> None:
        for i in tickets:
           self.__discard_pile.append(i) 
    
    def is_empty(self) -> bool:
        return len(self.__remaining_destinations) == 0
    
    def return_discarded_cards_to_main_deck(self) -> None:
        random.shuffle(self.__discard_pile)
        self.__remaining_destinations.extend(self.__discard_pile)
        self.__discard_pile = []
        return