import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

from src.utils.train_cards import MainTrainCardDeck, TrainCardType
from src.utils.constants import *

class TestMainTrainCardDeck(unittest.TestCase):

    def setUp(self):
        """Вызывается перед каждым тестом. Создаем чистый экземпляр колоды."""
        # Фиксируем random.seed, чтобы перемешивание в __init__ всегда было одинаковым
        import random
        random.seed(42)
        
        self.deck = MainTrainCardDeck()
        
        # Вручную инициализируем приватный список open_cards, 
        # так как в вашем __init__ его заполнение сейчас пропущено
        self.deck._MainTrainCardDeck__open_cards = [
            TrainCardType.WHITE, TrainCardType.BLACK, TrainCardType.YELLOW, 
            TrainCardType.GREEN, TrainCardType.BLUE
        ]
        self.deck._MainTrainCardDeck__discard_pile = []

    def test_init_deck_size(self):
        """Проверяем, что колода инициализируется с правильным количеством карт."""
        # 9 типов карт всего. 8 цветных + 1 локомотив.
        # Цветных карт: 8 * 12 = 96. Локомотивов: 14. Всего = 110.
        expected_total = (len(TrainCardType) - 1) * TRAIN_CARDS_PER_COLOR + LOCOMOTIVE_CARDS
        self.assertEqual(len(self.deck._MainTrainCardDeck__remaining_cards) 
                         + len(self.deck._MainTrainCardDeck__open_cards), 
                         expected_total)

    def test_draw_open_card_valid(self):
        """Проверяем успешное взятие открытой карты."""
        initial_remaining_count = len(self.deck._MainTrainCardDeck__remaining_cards)
        
        # Берем карту с индексом 1 (в setUp это BLACK)
        drawn_card = self.deck.take_open_card(1)
        
        self.assertEqual(drawn_card, TrainCardType.BLACK)
        # Проверяем, что из основной колоды ушла одна карта на замену открытой
        self.assertEqual(len(self.deck._MainTrainCardDeck__remaining_cards), initial_remaining_count - 1)

    def test_draw_open_card_invalid_index(self):
        """Проверяем, что при неверном индексе выбрасывается ошибка."""
        with self.assertRaises(ValueError):
            self.deck.take_open_card(99)  # Индекс явно больше разрешенного OPEN_CARDS - 1
            
        with self.assertRaises(ValueError):
            self.deck.take_open_card(-1)

    def test_draw_close_card(self):
        """Проверяем взятие карты в закрытую из колоды."""
        initial_count = len(self.deck._MainTrainCardDeck__remaining_cards)
        top_card = self.deck._MainTrainCardDeck__remaining_cards[-1]
        
        drawn_card = self.deck.take_close_card()
        
        self.assertEqual(drawn_card, top_card)
        self.assertEqual(len(self.deck._MainTrainCardDeck__remaining_cards), initial_count - 1)

    def test_discard_cards_adds_to_discard_pile(self):
        """Проверяем, что сброс отправляет карты в стопку сброса."""
        self.deck.discard_cards(number_of_normal_cards=2, type_of_normal_cards=TrainCardType.RED, number_of_locomotives=1)
        
        discard_pile = self.deck._MainTrainCardDeck__discard_pile
        self.assertEqual(len(discard_pile), 3)
        self.assertEqual(discard_pile.count(TrainCardType.RED), 2)
        self.assertEqual(discard_pile.count(TrainCardType.LOCOMOTIVE), 1)

    def test_return_discarded_cards_to_main_deck(self):
        """Проверяем замешивание сброса обратно в колоду, если она опустела."""
        # Опустошаем основную колоду
        self.deck._MainTrainCardDeck__remaining_cards = []
        # Наполняем сброс
        self.deck._MainTrainCardDeck__discard_pile = [TrainCardType.ORANGE, TrainCardType.PURPLE]
        
        # Триггерим вызов через метод проверки пустоты/добора
        self.deck.take_close_card()
        
        # В колоде должна остаться 1 карта (так как одну мы только что вытянули методом draw_close_card)
        self.assertEqual(len(self.deck._MainTrainCardDeck__remaining_cards), 1)
        self.assertEqual(len(self.deck._MainTrainCardDeck__discard_pile), 0)

    def test_open_cards_need_refresh_true(self):
        """Проверяем триггер обновления: 3 или более локомотива среди открытых карт."""
        self.deck._MainTrainCardDeck__open_cards = [
            TrainCardType.LOCOMOTIVE, TrainCardType.LOCOMOTIVE, TrainCardType.LOCOMOTIVE,
            TrainCardType.GREEN, TrainCardType.BLUE
        ]
        self.assertTrue(self.deck.open_cards_need_refresh())

    def test_open_cards_need_refresh_false(self):
        """Проверяем триггер обновления: локомотивов меньше 3."""
        self.deck._MainTrainCardDeck__open_cards = [
            TrainCardType.LOCOMOTIVE, TrainCardType.LOCOMOTIVE, TrainCardType.WHITE,
            TrainCardType.GREEN, TrainCardType.BLUE
        ]
        self.assertFalse(self.deck.open_cards_need_refresh())

if __name__ == '__main__':
    unittest.main()