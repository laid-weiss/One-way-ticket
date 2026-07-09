from enum import Enum
from utils.train_cards import TrainCardType
from utils.game_type import GeneralGameData
from utils.player import Player, PlayerAction, PlayerStatus
import utils.constants as constants

class PlayerStepFSMStates(Enum):
    IDLE = 0
    TakenFirstTrainCard = 1
    TakingRouteCards = 2
    Done = 3

class PlayerStepFSM:
    __player_data : Player
    __game_data : GeneralGameData
    __state : PlayerStepFSMStates

    def __init__(self, player_ID : int, game_data : GeneralGameData):
        self.__player_data = game_data.players[player_ID]
        self.__game_data = game_data
        self.__state = PlayerStepFSMStates.IDLE
        self.__states = {
            PlayerStepFSMStates.IDLE: self._handle_IDLE,
            PlayerStepFSMStates.TakenFirstTrainCard: self._handle_TakenFirstTrainCard,
            PlayerStepFSMStates.TakingRouteCards: self._handle_TakingRouteCards,
            PlayerStepFSMStates.Done: self._handle_Done,
        }

    def EOS(self):
        self.__player_data.Status = PlayerStatus.NotActive
        return PlayerStepFSMStates.Done


    def _handle_IDLE(self, event : PlayerAction, event_data) -> PlayerStepFSMStates:
        # Сбрасываем статус ошибки, если игрок делает новую попытку действия
        self.__player_data.Status = PlayerStatus.Active

        # --- 1. ОБНОВЛЕНИЕ ПАРКА (Первая карта) ---
        if event == PlayerAction.TakeOpenCard:
            # Предотвращаем выход за границы массива открытых карт
            if event_data > (constants.OPEN_CARDS - 1) or event_data < 0:
                self.__player_data.Status = PlayerStatus.ErrorInvalidAction
                return PlayerStepFSMStates.IDLE

            card: TrainCardType = self.__game_data.train_cards_deck.take_open_card(event_data)
            self.__player_data.train_deck.append(card)
            # Если взят открытый локомотив — ход завершается
            if card == TrainCardType.LOCOMOTIVE:
                return PlayerStepFSMStates.Done
            return PlayerStepFSMStates.TakenFirstTrainCard

        elif event == PlayerAction.TakeCloseCard:
            card: TrainCardType = self.__game_data.train_cards_deck.take_close_card()
            self.__player_data.train_deck.append(card)
            return PlayerStepFSMStates.TakenFirstTrainCard

        # --- 2. ПРОХОЖДЕНИЕ ПЕРЕГОНА ---
        elif event == PlayerAction.BuildPath:
            # event_data содержит: {'track_section': TrackSection, 'cards_to_spend': (normal_count, card_type, locomotive_count)}
            track = event_data['track_section']
            normal_cnt, card_type, loco_cnt = event_data['cards_to_spend']
            required_length = normal_cnt + loco_cnt

            # 1. Проверяем, хватает ли игроку пластиковых вагончиков (чипов) для строительства пути
            if self.__player_data.train_chips < required_length:
                # Предполагается, что вы добавили этот статус в PlayerStatus, как в предыдущем шаге
                self.__player_data.Status = PlayerStatus.ErrorInvalidAction  # Или создайте специальный статус вроде ErrorNotEnoughChips
                return PlayerStepFSMStates.IDLE

            # 2. Ищем свободный путь на данном отрезке (ищем первый элемент со значением 0)
            free_track_index = -1
            for idx, owner_id in enumerate(track.owner):
                if owner_id == 0:
                    free_track_index = idx
                    break

            # Если свободных путей на этом отрезке не осталось
            if free_track_index == -1:
                self.__player_data.Status = PlayerStatus.ErrorTrackAlreadyTaken
                return PlayerStepFSMStates.IDLE

            # TODO: Дополнительно для 2-3 игроков можно сделать проверку спаренных путей, 
            # если в вашей TrackSectionsMap они представлены разными объектами TrackSection.

            # 3. Списание карт, фиксация владельца пути и вычитание вагончиков
            # Передаем управление методу сброса карт
            for _ in range(normal_cnt):
                if card_type in self.__player_data.train_deck:
                    self.__player_data.train_deck.remove(card_type)
            
            # Затем удаляем использованные локомотивы
            for _ in range(loco_cnt):
                if TrainCardType.LOCOMOTIVE in self.__player_data.train_deck:
                    self.__player_data.train_deck.remove(TrainCardType.LOCOMOTIVE)
                
            self.__game_data.train_cards_deck.discard_cards(normal_cnt, card_type, loco_cnt)
       

            # Предположим, что у игрока есть уникальный ID. Если его нет в классе Player, 
            # можно использовать условную единицу или передавать id в автомат. 
            # Заменяем 0 на ID игрока (например, 1) по найденному индексу свободного пути
            track.owner[free_track_index] = self.__player_data.ID
            
            # Уменьшаем запас вагончиков у игрока
            self.__player_data.train_chips -= required_length
            
            return self.EOS()

        # --- 3. ВЫБОР НОВЫХ ЦЕЛЕЙ ---
        elif event == PlayerAction.TakeRouteCard:
            drawn_tickets = self.__game_data.destination_tickets_dec.draw_tickets()
            self.__player_data.temp_route_deck.extend(drawn_tickets)
            return PlayerStepFSMStates.TakingRouteCards

        self.__player_data.Status = PlayerStatus.ErrorInvalidAction
        return PlayerStepFSMStates.IDLE

    def _handle_TakenFirstTrainCard(self, event : PlayerAction, event_data) -> PlayerStepFSMStates:
        self.__player_data.Status = PlayerStatus.Active

        if event == PlayerAction.TakeOpenCard:
            # Заглядываем в массив открытых карт перед тем, как забрать
            open_cards = self.__game_data.train_cards_deck.get_open_cards()
            if open_cards[event_data] == TrainCardType.LOCOMOTIVE:
                self.__player_data.Status = PlayerStatus.ErrorLocomotiveSecondCard
                return PlayerStepFSMStates.TakenFirstTrainCard # Остаемся в этом же состоянии для повтора
                
            card: TrainCardType = self.__game_data.train_cards_deck.take_open_card(event_data)
            self.__player_data.train_deck.append(card)

            return self.EOS()

        elif event == PlayerAction.TakeCloseCard:
            card: TrainCardType = self.__game_data.train_cards_deck.take_close_card()
            self.__player_data.train_deck.append(card)

            return self.EOS()
        
        self.__player_data.Status = PlayerStatus.ErrorInvalidAction
        return PlayerStepFSMStates.TakenFirstTrainCard

    def _handle_TakingRouteCards(self, event : PlayerAction, event_data) -> PlayerStepFSMStates:
        self.__player_data.Status = PlayerStatus.Active

        if event == PlayerAction.ThrowRouteCard:
            # event_data: список DestinationTicket, отправляемый под низ колоды
            for ticket in event_data:
                if ticket in self.__player_data.temp_route_deck:
                    self.__player_data.temp_route_deck.remove(ticket)
                    self.__game_data.destination_tickets_dec.return_tickets(ticket)
            
            # Правило игры: нужно оставить себе хотя бы 1 карту маршрута
            if len(self.__player_data.temp_route_deck) < 1:
                self.__player_data.Status = PlayerStatus.ErrorNotEnoughRouteCards
                return PlayerStepFSMStates.TakingRouteCards
            
            # Переносим подтвержденные карты в руку игрока
            self.__player_data.route_deck.extend(self.__player_data.temp_route_deck)
            self.__player_data.temp_route_deck.clear()
            return self.EOS()
            
        self.__player_data.Status = PlayerStatus.ErrorInvalidAction
        return PlayerStepFSMStates.TakingRouteCards

    def _handle_Done(self, event : PlayerAction, event_data) -> PlayerStepFSMStates:
        return PlayerStepFSMStates.Done

    def StepDone(self) -> bool:
        return self.__state == PlayerStepFSMStates.Done  

    def dispatch(self, event : PlayerAction, event_data = None):
        if self.__state not in self.__states:
            self.__player_data.Status = PlayerStatus.ErrorInvalidAction
            return
        
        # Переключаем состояние на основе результата работы обработчика
        self.__state = self.__states[self.__state](event, event_data)