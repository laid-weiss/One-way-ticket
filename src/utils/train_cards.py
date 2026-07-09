from __future__ import annotations

from enum import Enum
import random

from . import constants


class TrainCardType(Enum):
    WHITE = 0
    BLACK = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    RED = 5
    ORANGE = 6
    PURPLE = 7
    LOCOMOTIVE = 8


type PlayerTrainCardDeck = list[TrainCardType]


class MainTrainCardDeck:
    __remaining_cards: list[TrainCardType]
    __discard_pile: list[TrainCardType]
    __open_cards: list[TrainCardType]

    def __init__(self) -> None:
        self.__remaining_cards = []
        self.__discard_pile = []
        self.__open_cards = []

        for i in range(len(TrainCardType) - 1):
            for _ in range(constants.TRAIN_CARDS_PER_COLOR):
                self.__remaining_cards.append(TrainCardType(i))

        for _ in range(constants.LOCOMOTIVE_CARDS):
            self.__remaining_cards.append(TrainCardType.LOCOMOTIVE)

        random.shuffle(self.__remaining_cards)
        for _ in range(constants.OPEN_CARDS):
            self.__open_cards.append(self._draw_replacement_card())

        if self.open_cards_need_refresh():
            self.open_cards_refresh()

    def _draw_replacement_card(self) -> TrainCardType:
        if self.is_empty():
            self.return_discarded_cards_to_main_deck()
        if self.is_empty():
            raise RuntimeError("Train cards deck and discard pile are empty")
        return self.__remaining_cards.pop()

    def _discard_open_card(self, index: int) -> TrainCardType:
        result = self.__open_cards[index]
        self.__open_cards[index] = self._draw_replacement_card()
        return result

    def take_open_card(self, index: int) -> TrainCardType:
        if index > (constants.OPEN_CARDS - 1) or index < 0:
            raise ValueError("Index of open card in train deck is invalid")

        result = self._discard_open_card(index)
        if self.open_cards_need_refresh():
            self.open_cards_refresh()
        return result

    def take_close_card(self) -> TrainCardType:
        return self._draw_replacement_card()

    def is_empty(self) -> bool:
        return len(self.__remaining_cards) == 0

    def discard_cards(
        self,
        number_of_normal_cards: int,
        type_of_normal_cards: TrainCardType,
        number_of_locomotives: int,
    ) -> None:
        for _ in range(number_of_normal_cards):
            self.__discard_pile.append(type_of_normal_cards)
        for _ in range(number_of_locomotives):
            self.__discard_pile.append(TrainCardType.LOCOMOTIVE)

    def return_discarded_cards_to_main_deck(self) -> None:
        random.shuffle(self.__discard_pile)
        self.__remaining_cards.extend(self.__discard_pile)
        self.__discard_pile = []

    def open_cards_need_refresh(self) -> bool:
        return self.__open_cards.count(TrainCardType.LOCOMOTIVE) >= 3

    def open_cards_refresh(self) -> None:
        # If three or more locomotives are face up, discard all five and replace.
        guard = 0
        while self.open_cards_need_refresh() and guard < 10:
            guard += 1
            old_open_cards = list(self.__open_cards)
            self.__discard_pile.extend(old_open_cards)
            self.__open_cards.clear()
            for _ in range(constants.OPEN_CARDS):
                self.__open_cards.append(self._draw_replacement_card())

    def get_open_cards(self) -> list[TrainCardType]:
        return self.__open_cards.copy()

    def remaining_count(self) -> int:
        return len(self.__remaining_cards)

    def discard_count(self) -> int:
        return len(self.__discard_pile)
