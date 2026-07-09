import unittest
from unittest.mock import MagicMock

# Импорты ваших модулей (подправьте пути, если они отличаются)
from utils.player import Player, PlayerStatus, PlayerAction
from utils.train_cards import TrainCardType
from utils.game_type import GeneralGameData
from utils.board import TrackSection
from utils.destination_tickets import DestinationTicket, DestinationTicketType, Destination

# Импорт тестируемого автомата
from model.player_step_fsm import PlayerStepFSM, PlayerStepFSMStates  

class TestPlayerStepFSM(unittest.TestCase):

    def setUp(self):
        # Создаем заглушки для игрока
        self.player = Player(
            ID = 1,
            Status=PlayerStatus.Active,
            train_deck=[],
            route_deck=[],
            temp_route_deck=[],
            train_chips=45,
            points=0
        )
        
        # Создаем заглушку для игровых данных и колод
        self.game_data = MagicMock(spec=GeneralGameData)
        self.game_data.train_cards_deck = MagicMock()
        self.game_data.destination_tickets_dec = MagicMock()
        self.game_data.players = [None, self.player]
        
        # Инициализируем автомат
        self.fsm = PlayerStepFSM(1, self.game_data)

    # --- ТЕСТЫ: ОБНОВЛЕНИЕ ПАРКА (КАРТЫ ПОЕЗДОВ) ---

    def test_take_two_close_cards_successfully(self):
        """Игрок успешно берет две карты вслепую из колоды."""
        self.game_data.train_cards_deck.take_close_card.side_effect = [
            TrainCardType.RED, TrainCardType.BLUE
        ]

        # Первая карта
        self.fsm.dispatch(PlayerAction.TakeCloseCard)
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.TakenFirstTrainCard)
        self.assertEqual(self.player.Status, PlayerStatus.Active)
        
        # Вторая карта
        self.fsm.dispatch(PlayerAction.TakeCloseCard)
        self.assertTrue(self.fsm.StepDone())
        self.assertEqual(self.player.train_deck, [TrainCardType.RED, TrainCardType.BLUE])

    def test_take_open_locomotive_first_card_ends_turn(self):
        """Если первая взятая открытая карта — локомотив, ход сразу завершается."""
        self.game_data.train_cards_deck.take_open_card.return_value = TrainCardType.LOCOMOTIVE

        self.fsm.dispatch(PlayerAction.TakeOpenCard, event_data=0)
        
        self.assertTrue(self.fsm.StepDone())
        self.assertEqual(self.player.train_deck, [TrainCardType.LOCOMOTIVE])
        self.assertEqual(self.player.Status, PlayerStatus.Active)

    def test_take_open_locomotive_second_card_fails(self):
        """Нельзя брать открытый локомотив второй картой."""
        # Первая карта — обычная закрытая
        self.game_data.train_cards_deck.take_close_card.return_value = TrainCardType.GREEN
        self.fsm.dispatch(PlayerAction.TakeCloseCard)

        # Мокаем, что на столе под индексом 2 лежит локомотив
        self.game_data.train_cards_deck.get_open_cards.return_value = [
            TrainCardType.RED, TrainCardType.WHITE, TrainCardType.LOCOMOTIVE
        ]

        # Пытаемся взять этот локомотив под индексом 2
        self.fsm.dispatch(PlayerAction.TakeOpenCard, event_data=2)

        # Автомат должен остаться в прежнем состоянии и записать ошибку в статус игрока
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.TakenFirstTrainCard)
        self.assertEqual(self.player.Status, PlayerStatus.ErrorLocomotiveSecondCard)

    # --- ТЕСТЫ: ПРОХОЖДЕНИЕ ПЕРЕГОНА ---

    def test_build_path_successfully(self):
        """Успешное занятие свободного перегона."""
        track = TrackSection(
            number_of_cards=(3),
            type_of_cards=(TrainCardType.RED),
            station1=Destination.LA,
            station2=Destination.DC,
            owner=[0]
        )
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (3, TrainCardType.RED, 0)
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        self.assertTrue(self.fsm.StepDone())
        self.assertEqual(track.owner, [1])  # Перегон занят игроком
        self.assertEqual(self.player.train_chips, 42)  # Вагончики списались (45 - 3)
        self.game_data.train_cards_deck.discard_cards.assert_called_once_with(3, TrainCardType.RED, 0)

    def test_build_path_already_taken(self):
        """Попытка занять уже занятый перегон вызывает ошибку в статусе."""
        track = TrackSection(
            number_of_cards=(2,),
            type_of_cards=(TrainCardType.BLUE,),
            station1=Destination.LA,
            station2=Destination.WA,
            owner=[99]  # Уже занят игроком 99
        )
        
        event_data = {
            'track_section': track,
            'cards_to_spend': (2, TrainCardType.BLUE, 0)
        }

        self.fsm.dispatch(PlayerAction.BuildPath, event_data=event_data)

        # Состояние должно остаться IDLE, статус игрока меняется на ошибку
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.IDLE)
        self.assertEqual(self.player.Status, PlayerStatus.ErrorTrackAlreadyTaken)

    # --- ТЕСТЫ: ВЫБОР НОВЫХ ЦЕЛЕЙ ---

    def test_take_route_cards_and_keep_two(self):
        """Игрок берет 3 карты маршрутов и оставляет себе 2 (сбрасывает 1)."""
        ticket1 = DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.DC, 10)
        ticket2 = DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.WA, 5)
        ticket3 = DestinationTicket(DestinationTicketType.LONG, Destination.DC, Destination.WA, 15)
        
        self.game_data.destination_tickets_dec.draw_tickets.return_value = [ticket1, ticket2, ticket3]

        # Тянем карты целей
        self.fsm.dispatch(PlayerAction.TakeRouteCard)
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.TakingRouteCards)
        self.assertEqual(self.player.temp_route_deck, [ticket1, ticket2, ticket3])

        # Сбрасываем билет №3 (ticket3)
        self.fsm.dispatch(PlayerAction.ThrowRouteCard, event_data=[ticket3])

        # Ход завершен, в руке остались 1 и 2, временный карман пуст
        self.assertTrue(self.fsm.StepDone())
        self.assertEqual(self.player.route_deck, [ticket1, ticket2])
        self.assertEqual(self.player.temp_route_deck, [])
        self.game_data.destination_tickets_dec.return_tickets.assert_called_once_with(ticket3)

    def test_throw_all_route_cards_fails(self):
        """Игрок пытается сбросить все 3 карты, что запрещено правилами."""
        ticket1 = DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.DC, 10)
        ticket2 = DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.WA, 5)
        ticket3 = DestinationTicket(DestinationTicketType.LONG, Destination.DC, Destination.WA, 15)
        
        self.game_data.destination_tickets_dec.draw_tickets.return_value = [ticket1, ticket2, ticket3]

        self.fsm.dispatch(PlayerAction.TakeRouteCard)
        
        # Пытаемся сбросить вообще все взятые билеты
        self.fsm.dispatch(PlayerAction.ThrowRouteCard, event_data=[ticket1, ticket2, ticket3])

        # Автомат не должен пустить в Done, статус переключается на ошибку
        self.assertEqual(self.fsm._PlayerStepFSM__state, PlayerStepFSMStates.TakingRouteCards)
        self.assertEqual(self.player.Status, PlayerStatus.ErrorNotEnoughRouteCards)


if __name__ == '__main__':
    unittest.main()