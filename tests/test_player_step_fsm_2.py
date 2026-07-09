import unittest
from unittest.mock import MagicMock

# Импорты ваших игровых модулей
from utils.player import Player, PlayerStatus, PlayerAction
from utils.train_cards import TrainCardType
from utils.game_type import GeneralGameData
from utils.board import TrackSection
from utils.destination_tickets import Destination

# Предполагается, что ваш автомат находится в файле player_step_fsm.py
from model.player_step_fsm import PlayerStepFSM, PlayerStepFSMStates 


class TestPlayerStepFSMPathBuilding(unittest.TestCase):

    def setUp(self):
        # Создаем заглушку для игрока и добавляем динамическое поле ID, раз оно требуется в FSM
        self.player = Player(
            ID = 1,
            Status=PlayerStatus.Active,
            train_deck=[],
            route_deck=[],
            temp_route_deck=[],
            train_chips=45,
            points=0
        )
       
        # Создаем заглушку для игровых данных
        self.game_data = MagicMock(spec=GeneralGameData)
        self.game_data.train_cards_deck = MagicMock()
        self.game_data.players = [None, self.player]
        
        # Инициализируем автомат
        self.fsm = PlayerStepFSM(1, self.game_data)
        

    def test_build_path_first_free_lane_success(self):
        """Успешное занятие ПЕРВОГО пути на спаренном перегоне (оба свободны: [0, 0])."""
        track = TrackSection(
            number_of_cards=(3,),
            type_of_cards=(TrainCardType.RED,),
            station1=Destination.LA,
            station2=Destination.DC,
            owner=[0, 0]  # Двойной перегон, оба пути свободны
        )
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (3, TrainCardType.RED, 0) # 3 обычные карты
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        # Проверяем, что первый свободный путь (индекс 0) теперь принадлежит игроку 42
        self.assertEqual(track.owner, [1, 0])
        self.assertEqual(self.player.train_chips, 42)  # 45 - 3 = 42 вагончика осталось
        self.assertTrue(self.fsm.StepDone())
        self.assertEqual(self.player.Status, PlayerStatus.NotActive)

    def test_build_path_second_lane_success(self):
        """Успешное занятие ВТОРОГО пути, если первый уже занят другим игроком ([99, 0])."""
        track = TrackSection(
            number_of_cards=(2,),
            type_of_cards=(TrainCardType.BLUE,),
            station1=Destination.LA,
            station2=Destination.WA,
            owner=[99, 0]  # Первый путь занят игроком 99, второй свободен
        )
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (2, TrainCardType.BLUE, 0)
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        # Проверяем, что занят именно второй путь (индекс 1)
        self.assertEqual(track.owner, [99, 1])
        self.assertEqual(self.player.train_chips, 43)  # 45 - 2 = 43 вагончика осталось
        self.assertTrue(self.fsm.StepDone())

    def test_build_path_not_enough_chips(self):
        """Попытка построить путь, если у игрока не хватает вагончиков (chips)."""
        track = TrackSection(
            number_of_cards=(5,),
            type_of_cards=(TrainCardType.BLACK,),
            station1=Destination.DC,
            station2=Destination.WA,
            owner=[0]  # Путь свободен
        )
        
        # Искусственно уменьшаем количество вагончиков у игрока до 3
        self.player.train_chips = 3
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (5, TrainCardType.BLACK, 0)  # Требуется 5 вагончиков
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        # Проверяем, что автомат остался в состоянии IDLE, а игроку выставлен статус ошибки
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.IDLE)
        self.assertEqual(self.player.Status, PlayerStatus.ErrorInvalidAction)
        self.assertEqual(track.owner, [0])  # Путь остался нетронутым

    def test_build_path_no_free_lanes_left(self):
        """Попытка занять перегон, на котором все пути уже выкуплены ([11, 22])."""
        track = TrackSection(
            number_of_cards=(4,),
            type_of_cards=(TrainCardType.GREEN,),
            station1=Destination.LA,
            station2=Destination.DC,
            owner=[11, 22]  # Оба пути заняты другими игроками
        )
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (4, TrainCardType.GREEN, 0)
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        # Автомат должен остаться в состоянии IDLE, а игроку присвоен статус ErrorTrackAlreadyTaken
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.IDLE)
        self.assertEqual(self.player.Status, PlayerStatus.ErrorTrackAlreadyTaken)
        self.assertEqual(track.owner, [11, 22])  # Владельцы не изменились


if __name__ == '__main__':
    unittest.main()