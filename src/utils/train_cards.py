from dataclasses import dataclass
from enum import Enum
from . import constants
import random

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
    __remaining_cards : list[TrainCardType]
    __discard_pile : list[TrainCardType]
    __open_cards : list[TrainCardType]

    def __init__(self) -> None:
        # 1. ОБЯЗАТЕЛЬНО инициализируем все списки пустыми значениями
        self.__remaining_cards = []
        self.__discard_pile = []  # Теперь и сброс не упадет в будущем
        self.__open_cards = []     # Создаем пустой список для открытых карт

        # 2. Заполняем колоду цветными картами
        for i in range(len(TrainCardType) - 1):
            for j in range(constants.TRAIN_CARDS_PER_COLOR):
                self.__remaining_cards.append(TrainCardType(i))
                
        # 3. Добавляем локомотивы
        for i in range(constants.LOCOMOTIVE_CARDS):
            self.__remaining_cards.append(TrainCardType.LOCOMOTIVE)
            
        # 4. Перемешиваем
        random.shuffle(self.__remaining_cards)

        # 5. Теперь .append() сработает идеально, так как список уже существует!
        for i in range(constants.OPEN_CARDS):
            self.__open_cards.append(self.__remaining_cards.pop())

        return
    
    def discard_open_card(self, index : int) -> TrainCardType:
        result = self.__open_cards[index]
        self.__open_cards[index] = self.__remaining_cards.pop()
        if (self.is_empty()):
            self.return_discarded_cards_to_main_deck()
        return result

    def draw_open_card(self, index : int) -> TrainCardType:
        if(index > (constants.OPEN_CARDS - 1) or index < 0) :
            raise ValueError("Index of open card in train deck is invalid")

        result = self.discard_open_card(index)
        if (self.open_cards_need_refresh()):
            self.open_cards_refresh()
        return result

    def draw_close_card(self) -> TrainCardType:
        if (self.is_empty()):
            self.return_discarded_cards_to_main_deck()
        return self.__remaining_cards.pop()
    
    def is_empty(self) -> bool:
        return len(self.__remaining_cards) == 0
    
    def discard_cards(self, number_of_normal_cards : int, 
                      type_of_normal_cards : TrainCardType, number_of_locomotives : int) -> None:
        for i in range(number_of_normal_cards) :
            self.__discard_pile.append(type_of_normal_cards)
        for i in range(number_of_locomotives):
            self.__discard_pile.append(TrainCardType.LOCOMOTIVE)
        return

    def return_discarded_cards_to_main_deck(self) -> None:
        random.shuffle(self.__discard_pile)
        self.__remaining_cards.extend(self.__discard_pile)
        self.__discard_pile = []
        return
    
    def open_cards_need_refresh(self) -> bool:
        count = 0
        for i in range(constants.OPEN_CARDS) :
            if (self.__open_cards[i] == TrainCardType.LOCOMOTIVE):
                count += 1
        return count >= 3
    
    def open_cards_refresh(self) -> None:
        for i in range(constants.OPEN_CARDS):
            self.discard_open_card(i)
        if (self.open_cards_need_refresh()):
            self.open_cards_refresh()
        return
    
    def get_open_cards(self) -> list[TrainCardType] :
        return self.__open_cards.copy()

    