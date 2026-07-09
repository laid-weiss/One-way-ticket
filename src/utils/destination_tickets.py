from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random

from . import constants


class DestinationTicketType(Enum):
    LONG = 0
    SHORT = 1


class Destination(Enum):
    Vancouver = 0
    Calgary = 1
    Seattle = 2
    Portland = 3
    Helena = 4
    San_Francisco = 5
    Los_Angeles = 6
    Las_Vegas = 7
    Phoenix = 8
    El_Paso = 9
    Denver = 10
    Santa_Fe = 11
    Winnipeg = 12
    Duluth = 13
    Omaha = 14
    Kansas_City = 15
    Saint_Louis = 16
    Dallas = 17
    Houston = 18
    New_Orlean = 19
    Little_Rock = 20
    Miami = 21
    Charleston = 22
    Atlanta = 23
    Nashville = 24
    Chicago = 25
    Pittsburgh = 26
    Charlesto = 27
    Raleigh = 28
    Washington = 29
    New_York = 30
    Boston = 31
    Montreal = 32
    Sault_Ste_Marie = 33
    Salt_Lake_City = 35
    Toronto = 36
    Oklahoma_City = 37
    



@dataclass(frozen=True)
class DestinationTicket:
    type: DestinationTicketType
    start: Destination
    finish: Destination
    price: int


# Compact deck for the current prototype. It is intentionally bigger than the
# old two-card placeholder so four local players can receive initial tickets.
ALL_DESTINATION_TICKETS = [
    DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.DC, 10),
    DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.WA, 5),
    DestinationTicket(DestinationTicketType.SHORT, Destination.WA, Destination.DC, 8),
    DestinationTicket(DestinationTicketType.SHORT, Destination.SF, Destination.DEN, 7),
    DestinationTicket(DestinationTicketType.SHORT, Destination.DEN, Destination.CHI, 6),
    DestinationTicket(DestinationTicketType.SHORT, Destination.CHI, Destination.NY, 6),
    DestinationTicket(DestinationTicketType.SHORT, Destination.ATL, Destination.MIA, 5),
    DestinationTicket(DestinationTicketType.SHORT, Destination.NY, Destination.DC, 4),
    DestinationTicket(DestinationTicketType.LONG, Destination.SEA, Destination.MIA, 20),
    DestinationTicket(DestinationTicketType.LONG, Destination.LA, Destination.NY, 21),
    DestinationTicket(DestinationTicketType.LONG, Destination.SF, Destination.ATL, 17),
    DestinationTicket(DestinationTicketType.LONG, Destination.SEA, Destination.DC, 18),
    DestinationTicket(DestinationTicketType.LONG, Destination.LA, Destination.MIA, 19),
    DestinationTicket(DestinationTicketType.LONG, Destination.DEN, Destination.DC, 12),
]

type PlayerDestinationTicketDeck = list[DestinationTicket]


class MainDestinationTicketDeck:
    __remaining_destinations: list[DestinationTicket]
    __discard_pile: list[DestinationTicket]

    def __init__(self, shuffle: bool = True):
        self.__remaining_destinations = list(ALL_DESTINATION_TICKETS)
        self.__discard_pile = []
        if shuffle:
            random.shuffle(self.__remaining_destinations)

    def draw_tickets(self, count: int = constants.DRAW_DESTINATION_TICKETS) -> list[DestinationTicket]:
        """Draw up to `count` top route tickets. If fewer are left, return all left."""
        result: list[DestinationTicket] = []
        for _ in range(count):
            if self.is_empty():
                break
            result.append(self.__remaining_destinations.pop())
        return result

    def return_tickets(self, *tickets: DestinationTicket) -> None:
        """Return refused tickets under the route deck, face down."""
        for ticket in tickets:
            self.__remaining_destinations.insert(0, ticket)

    def is_empty(self) -> bool:
        return len(self.__remaining_destinations) == 0

    def return_discarded_cards_to_main_deck(self) -> None:
        # Backward-compatible API: old code called this name. In the final rules,
        # refused destination tickets are placed under the deck instead of shuffled.
        random.shuffle(self.__discard_pile)
        self.__remaining_destinations = self.__discard_pile + self.__remaining_destinations
        self.__discard_pile = []

    def remaining_count(self) -> int:
        return len(self.__remaining_destinations)
