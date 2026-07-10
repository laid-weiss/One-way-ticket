from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional
import random

try:  # Works when imported as src.model.game_model
    from ..utils import constants
    from ..utils.destination_tickets import Destination, DestinationTicket, MainDestinationTicketDeck
    from ..utils.game_settings import GameSettings, Settings, default_settings
    from ..utils.player import Player, PlayerStatus, PlayerType, TRAIN_CHIP_COLOR
    from ..utils.train_cards import MainTrainCardDeck, TrainCardType
except ImportError:  # Works with tests adding src to PYTHONPATH and importing model.game_model
    from utils import constants
    from utils.destination_tickets import Destination, DestinationTicket, MainDestinationTicketDeck
    from utils.game_settings import GameSettings, Settings, default_settings
    from utils.player import Player, PlayerStatus, PlayerType, TRAIN_CHIP_COLOR
    from utils.train_cards import MainTrainCardDeck, TrainCardType


TRAIN_CARD_BUTTON_ORDER = [
    TrainCardType.WHITE,
    TrainCardType.BLACK,
    TrainCardType.YELLOW,
    TrainCardType.GREEN,
    TrainCardType.BLUE,
    TrainCardType.RED,
    TrainCardType.ORANGE,
    TrainCardType.PURPLE,
    TrainCardType.LOCOMOTIVE,
]

ROUTE_POINTS_BY_LENGTH = {
    1: 1,
    2: 2,
    3: 4,
    4: 7,
    5: 10,
    6: 15,
}

# Map-local city points, measured in unscaled pixels from the top-left corner of
# assets/map/map.png. Change these when the map art is finalized.
CITY_POINTS_TOP_LEFT: dict[Destination, tuple[int, int]] = {
    Destination.Vancouver: (29, 19),
    Destination.Seattle: (24, 36),
    Destination.Calgary: (50, 18),
    Destination.Portland: (18, 49),
    Destination.Helena: (65, 49),
    Destination.Salt_Lake_City: (51, 77),
    Destination.San_Francisco: (13, 95),
    Destination.Los_Angeles: (23, 126),
    Destination.Phoenix: (50, 127),
    Destination.El_Paso: (75, 135),
    Destination.Las_Vegas: (39, 110),
    Destination.Winnipeg: (86, 20),
    Destination.Boston: (177, 32),
    Destination.Montreal: (166, 16),
    Destination.Toronto: (155, 37),
    Destination.Sault_Ste_Marie: (131, 30),
    Destination.Duluth: (108, 47),
    Destination.Denver: (76, 89),
    Destination.Santa_Fe: (74, 113),
    Destination.Houston: (116, 142),
    Destination.Dallas: (108, 130),
    Destination.Miami: (168, 156),
    Destination.Charleston: (170, 106),
    Destination.Raleigh: (164, 87),
    Destination.Washington: (173, 71),
    Destination.New_York: (172, 49),
    Destination.Pittsburgh: (154, 58),
    Destination.Atlanta: (153, 102),
    Destination.Oklahoma_City: (103, 106),
    Destination.Kansas_City: (106, 82),
    Destination.Omaha: (104, 70),
    Destination.Saint_Louis: (124, 87),
    Destination.Little_Rock: (130, 104),
    Destination.Nashville: (140, 93),
    Destination.Chicago: (129, 64)  
}

class TurnPhase(Enum):
    WAITING_FOR_ACTION = "waiting_for_action"
    TOOK_FIRST_TRAIN_CARD = "took_first_train_card"
    CHOOSING_DESTINATION_TICKETS = "choosing_destination_tickets"
    GAME_OVER = "game_over"


@dataclass(frozen=True)
class RectPx:
    """A rectangle in unscaled design pixels, with y measured from bottom."""

    left: int
    bottom: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def top(self) -> int:
        return self.bottom + self.height

    @property
    def center_x(self) -> float:
        return self.left + self.width / 2

    @property
    def center_y(self) -> float:
        return self.bottom + self.height / 2

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    @classmethod
    def from_top_left(cls, left: int, top: int, width: int, height: int) -> "RectPx":
        origin_x, origin_y = constants.GAME_UI_ORIGIN_TOP_LEFT_PIXELS
        absolute_left = origin_x + left
        absolute_top = origin_y + top
        bottom = constants.SCREEN_HEIGHT_IN_PIXELS - absolute_top - height
        return cls(absolute_left, bottom, width, height)


@dataclass(frozen=True)
class ChipDrawSpec:
    """Single wagon sprite placement on the map.

    x/y are map-local top-left coordinates in unscaled pixels. frame_index is a
    zero-based GIF frame number. Editing these values is the developer-facing way
    to tune each wagon's position and angle.
    """

    x: int
    y: int
    frame_index: int

    @property
    def rect(self) -> RectPx:
        map_left, map_top = constants.MAP_TOP_LEFT_PIXELS
        chip_w, chip_h = constants.TRAIN_CHIP_SIZE_PIXELS
        return RectPx.from_top_left(map_left + self.x, map_top + self.y, chip_w, chip_h)


@dataclass
class RouteTrack:
    id: str
    station1: Destination
    station2: Destination
    length: int
    color: Optional[TrainCardType]
    chips: list[ChipDrawSpec]
    owner: int = 0
    double_group: Optional[str] = None

    def cities(self) -> frozenset[Destination]:
        return frozenset((self.station1, self.station2))


@dataclass(frozen=True)
class CardButtonState:
    card_type: TrainCardType
    count: int
    rect: RectPx
    selected: bool = False


@dataclass(frozen=True)
class OpenTrainCardState:
    index: int
    card_type: TrainCardType
    rect: RectPx


@dataclass(frozen=True)
class RouteCardState:
    index: int
    ticket: DestinationTicket
    rect: RectPx
    hovered: bool = False
    selected: bool = True


@dataclass(frozen=True)
class PlayerPlateState:
    player_id: int
    rect: RectPx
    is_active: bool
    is_present: bool
    remaining_train_chips: int = 0
    points: int = 0
    chip_color: TRAIN_CHIP_COLOR = TRAIN_CHIP_COLOR.RED


@dataclass(frozen=True)
class ActionResult:
    success: bool
    message: str = ""
    turn_ended: bool = False


@dataclass
class FinalScoreSummary:
    completed_tickets: dict[int, int] = field(default_factory=dict)
    longest_roads: dict[int, int] = field(default_factory=dict)
    longest_bonus_player_ids: list[int] = field(default_factory=list)
    winner_ids: list[int] = field(default_factory=list)


# Prototype route layout. Coordinates come from assets/docs/table.md and can be
# replaced without touching controller/view code.
# _DEFAULT_TRACK_CHIP_ROWS = [
#     ((17, 18, 8), (10, 33, 7), (17, 36, 7)),
#     ((32, 9, 1), (49, 5, 3), (60, 2, 1), (72, 5, 16)),
#     ((25, 24, 4), (35, 17, 6), (49, 18, 13), (55, 31, 12)),
#     ((73, 19, 8), (66, 30, 8), (89, 12, 18), (103, 14, 17)),
#     ((115, 18, 16), (116, 26, 5), (106, 33, 4), (92, 39, 17)),
#     ((79, 38, 1), (66, 39, 1), (48, 38, 16), (37, 35, 17), (25, 36, 3)),
# ]

_DEFAULT_TRACK_CHIP_ROWS = [
    # Manually grouped rows based on the provided example (Items 1-24)
    ((17, 18, 8),), # vancouver-seatle
    ((10, 33, 7),), #seatle-portland
    ((17, 36, 7),), #seatle-portland
    ((32, 9, 1),), # vancouver-calgary
    ((49, 5, 3), (60, 2, 1), (72, 5, 16)), #calgary-winnipeg
    ((25, 24, 4), (35, 17, 6)), #calgary-seatle
    ((49, 18, 13), (55, 31, 12)), #calgary-helena
    ((73, 19, 8), (66, 30, 8)), # winnipegg-helena
    ((89, 12, 18), (103, 14, 17), (115, 18, 16)), # winnipeg - sault-ste-marie
    ((116, 26, 5), (106, 33, 4)), # sault-ste-maire - dulith
    ((92, 39, 17), (79, 38, 1), (66, 39, 1)), # dulith-helena
    ((48, 38, 16), (37, 35, 17), (25, 36, 3)), #helena - portland
    
    # Sequentially grouped remainder of the table (Items 25-94)
    ((4, 48, 6), (-1, 59, 9), (-2, 71, 10), (1, 82, 13)),  # portland - sac-francisco
    ((10, 51, 12), (7, 61, 9), (6, 70, 9), (7, 78, 8)), # portland - sac-francisco
    ((20, 43, 17), (30, 47, 15), (38, 54, 14), (42, 63, 11)), # portland - salt-lake-city
    ((51, 48, 7), (49, 60, 8)), # helena - salt-lake-city
    ((61, 49, 12), (65, 61, 12), (68, 72, 11)), # helena - denver
    ((61, 76, 16), (51, 71, 16)), # salt-lake-city - denver
    ((50, 77, 15), (60, 81, 2)), # salt-lake-city - denver
    ((75, 74, 5), (85, 66, 4)), # denver - omaha 
    ((90, 57, 15), (80, 51, 16), (69, 46, 17)), # omaha - helena
    ((99, 46, 8), (97, 57, 12)), # omaha - dulith
    ((103, 57, 7), (114, 55, 17)), # omaha - chicago
    ((118, 50, 15), (108, 44, 16)), # chicago - dulith
    ((110, 36, 3), (120, 34, 2), (131, 33, 17), (140, 33, 2)), # dulith - toronto
    ((130, 16, 5), (140, 10, 3) ,(150, 8, 1)), # sault-ste-marie - montreal
    ((131, 23, 2), (141, 25, 16)), # sault-ste-marie - toronto
    ((152, 12, 6), (148, 21, 8)), # montreal - toronto
    ((168, 15, 15),), # monreal - boston
    ((163, 19, 13),), # monreal - boston
    ((169, 34, 9),), # boston - new york
    ((164, 32, 8),), # boston - new york
    ((155, 46, 5),), # new york - pittsburgh
    ((165, 52, 12),), # new york - washington
    ((149, 56, 14), (158, 61, 17)), # washington - pittsburgh
    ((140, 48, 3), (128, 51, 6)), # pittsburgh - chicago
    ((117, 68, 9), (124, 73, 5), (132, 63, 7)), # chicago - saint louis
    ((140, 55, 7), (132, 63, 8), (124, 72, 4)), # saint louis - pittsburgh
    ((161, 71, 6), (164, 84, 14), (166, 92, 6)),# washington - raleigh
    ((154, 95, 17),), # charleson - atlanta
    ((140, 90, 16),), # atlanta - nashville
    ((151, 86, 7),), # nashville - raleigh
    ((125, 82, 17),), # nashville - saint louis
    ((128, 91, 5),), # nashville - little rock
    ((120, 88, 13),), # little rock - saint louis
    ((115, 94, 16), (103, 94, 4)), #little rock - oklahoma city
    ((104, 101, 16), (114, 101, 14)), #little rock - oklahoma city
    ((17, 84, 3), (28, 79, 4), (38, 75, 5)) # san francisco - salt lake city
]


def _chips(rows: list[tuple[int, int, int]]) -> list[ChipDrawSpec]:
    return [ChipDrawSpec(x, y, max(0, frame - 1)) for x, y, frame in rows]


# def build_default_tracks() -> list[RouteTrack]:
#     return [
#         RouteTrack("la-wa-a", Destination.LA, Destination.WA, 3, TrainCardType.YELLOW, _chips(*_DEFAULT_TRACK_CHIP_ROWS[0]), double_group="la-wa"),
#         RouteTrack("la-wa-b", Destination.LA, Destination.WA, 4, TrainCardType.GREEN, _chips(*_DEFAULT_TRACK_CHIP_ROWS[1]), double_group="la-wa"),
#         RouteTrack("la-den", Destination.LA, Destination.DEN, 4, None, _chips(*_DEFAULT_TRACK_CHIP_ROWS[2])),
#         RouteTrack("den-chi", Destination.DEN, Destination.CHI, 4, TrainCardType.ORANGE, _chips(*_DEFAULT_TRACK_CHIP_ROWS[3])),
#         RouteTrack("chi-dc", Destination.CHI, Destination.DC, 4, TrainCardType.BLUE, _chips(*_DEFAULT_TRACK_CHIP_ROWS[4])),
#         RouteTrack("wa-dc", Destination.WA, Destination.DC, 5, TrainCardType.BLACK, _chips(*_DEFAULT_TRACK_CHIP_ROWS[5])),
#     ]

def build_default_tracks() -> list[RouteTrack]:
    return [
        RouteTrack("vancouver-seattle", Destination.Vancouver, Destination.Seattle, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[0])),
        
        RouteTrack("seattle-portland-a", Destination.Seattle, Destination.Portland, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[1]), double_group="seattle-portland"),
        RouteTrack("seattle-portland-b", Destination.Seattle, Destination.Portland, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[2]), double_group="seattle-portland"),
        
        RouteTrack("vancouver-calgary", Destination.Vancouver, Destination.Calgary, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[3])),
        RouteTrack("calgary-winnipeg", Destination.Calgary, Destination.Winnipeg, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[4])),
        RouteTrack("calgary-seattle", Destination.Calgary, Destination.Seattle, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[5])),
        RouteTrack("calgary-helena", Destination.Calgary, Destination.Helena, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[6])),
        RouteTrack("winnipeg-helena", Destination.Winnipeg, Destination.Helena, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[7])),
        RouteTrack("winnipeg-sault-ste-marie", Destination.Winnipeg, Destination.Sault_Ste_Marie, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[8])),
        RouteTrack("sault-ste-marie-duluth", Destination.Sault_Ste_Marie, Destination.Duluth, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[9])),
        RouteTrack("duluth-helena", Destination.Duluth, Destination.Helena, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[10])),
        RouteTrack("helena-portland", Destination.Helena, Destination.Portland, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[11])),
        
        RouteTrack("portland-san-francisco-a", Destination.Portland, Destination.San_Francisco, 4, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[12]), double_group="portland-san-francisco"),
        RouteTrack("portland-san-francisco-b", Destination.Portland, Destination.San_Francisco, 4, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[13]), double_group="portland-san-francisco"),
        
        RouteTrack("portland-salt-lake-city", Destination.Portland, Destination.Salt_Lake_City, 4, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[14])),
        RouteTrack("helena-salt-lake-city", Destination.Helena, Destination.Salt_Lake_City, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[15])),
        RouteTrack("helena-denver", Destination.Helena, Destination.Denver, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[16])),
        
        RouteTrack("salt-lake-city-denver-a", Destination.Salt_Lake_City, Destination.Denver, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[17]), double_group="salt-lake-city-denver"),
        RouteTrack("salt-lake-city-denver-b", Destination.Salt_Lake_City, Destination.Denver, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[18]), double_group="salt-lake-city-denver"),
        
        RouteTrack("denver-omaha", Destination.Denver, Destination.Omaha, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[19])),
        RouteTrack("omaha-helena", Destination.Omaha, Destination.Helena, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[20])),
        RouteTrack("omaha-duluth", Destination.Omaha, Destination.Duluth, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[21])),
        RouteTrack("omaha-chicago", Destination.Omaha, Destination.Chicago, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[22])),
        RouteTrack("chicago-duluth", Destination.Chicago, Destination.Duluth, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[23])),
        RouteTrack("duluth-toronto", Destination.Duluth, Destination.Toronto, 4, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[24])),
        RouteTrack("sault-ste-marie-montreal", Destination.Sault_Ste_Marie, Destination.Montreal, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[25])),
        RouteTrack("sault-ste-marie-toronto", Destination.Sault_Ste_Marie, Destination.Toronto, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[26])),
        RouteTrack("montreal-toronto", Destination.Montreal, Destination.Toronto, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[27])),
        
        RouteTrack("montreal-boston-a", Destination.Montreal, Destination.Boston, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[28]), double_group="montreal-boston"),
        RouteTrack("montreal-boston-b", Destination.Montreal, Destination.Boston, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[29]), double_group="montreal-boston"),
        
        RouteTrack("boston-new-york-a", Destination.Boston, Destination.New_York, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[30]), double_group="boston-new-york"),
        RouteTrack("boston-new-york-b", Destination.Boston, Destination.New_York, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[31]), double_group="boston-new-york"),
        
        RouteTrack("new-york-pittsburgh", Destination.New_York, Destination.Pittsburgh, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[32])),
        RouteTrack("new-york-washington", Destination.New_York, Destination.Washington, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[33])),
        RouteTrack("washington-pittsburgh", Destination.Washington, Destination.Pittsburgh, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[34])),
        RouteTrack("pittsburgh-chicago", Destination.Pittsburgh, Destination.Chicago, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[35])),
        RouteTrack("chicago-saint-louis", Destination.Chicago, Destination.Saint_Louis, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[36])),
        RouteTrack("saint-louis-pittsburgh", Destination.Saint_Louis, Destination.Pittsburgh, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[37])),
        RouteTrack("washington-raleigh", Destination.Washington, Destination.Raleigh, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[38])),
        RouteTrack("charleston-atlanta", Destination.Charleston, Destination.Atlanta, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[39])),
        RouteTrack("atlanta-nashville", Destination.Atlanta, Destination.Nashville, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[40])),
        RouteTrack("nashville-raleigh", Destination.Nashville, Destination.Raleigh, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[41])),
        RouteTrack("nashville-saint-louis", Destination.Nashville, Destination.Saint_Louis, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[42])),
        RouteTrack("nashville-little-rock", Destination.Nashville, Destination.Little_Rock, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[43])),
        RouteTrack("little-rock-saint-louis", Destination.Little_Rock, Destination.Saint_Louis, 1, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[44])),
        
        RouteTrack("little-rock-oklahoma-city-a", Destination.Little_Rock, Destination.Oklahoma_City, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[45]), double_group="little-rock-oklahoma-city"),
        RouteTrack("little-rock-oklahoma-city-b", Destination.Little_Rock, Destination.Oklahoma_City, 2, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[46]), double_group="little-rock-oklahoma-city"),
        RouteTrack("salt-lake-city-san-francisco", Destination.Salt_Lake_City, Destination.San_Francisco, 3, None, _chips(_DEFAULT_TRACK_CHIP_ROWS[47]))

    ]


class GameModel:
    """Arcade-free game state and rules for the main Ticket to Ride scene."""

    def __init__(self, settings: GameSettings | Settings | None = None, random_seed: int | None = None):
        if random_seed is not None:
            random.seed(random_seed)

        self.settings = self._unwrap_settings(settings)
        self.number_of_players = max(
            constants.MIN_PLAYERS,
            min(constants.MAX_PLAYERS, self.settings.number_of_players),
        )
        self.train_cards_deck = MainTrainCardDeck()
        self.destination_tickets_deck = MainDestinationTicketDeck()
        self.players = self._create_players()
        self.tracks: list[RouteTrack] = build_default_tracks()

        self.current_player_index = 0
        self.phase = TurnPhase.WAITING_FOR_ACTION
        self.train_cards_taken_this_turn = 0
        self.selected_train_card_type: TrainCardType | None = None
        self.hovered_route_card_index: int | None = None
        self.hovered_track_id: str | None = None
        self.destination_ticket_keep_indices: set[int] = set()
        self.last_message = ""
        self.final_turns_remaining: int | None = None
        self.final_score_summary = FinalScoreSummary()
        self.final_scores_applied = False

        self._deal_initial_cards()
        self._activate_current_player()

    @staticmethod
    def _unwrap_settings(settings: GameSettings | Settings | None) -> Settings:
        if isinstance(settings, GameSettings):
            return settings.get_settings
        if isinstance(settings, Settings):
            return settings
        return default_settings()

    def _create_players(self) -> list[Player]:
        colors = list(self.settings.chip_colors)
        defaults = list(TRAIN_CHIP_COLOR)
        while len(colors) < self.number_of_players:
            colors.append(defaults[len(colors) % len(defaults)])

        players: list[Player] = []
        for index in range(self.number_of_players):
            players.append(
                Player(
                    ID=index + 1,
                    Status=PlayerStatus.NotActive,
                    train_deck=[],
                    route_deck=[],
                    temp_route_deck=[],
                    remaining_train_chips=constants.REMAINING_TRAIN_CHIPS_PER_PLAYER,
                    points=0,
                    type=PlayerType.LOCALPLAYER,
                    chip_color=colors[index],
                )
            )
        return players

    def _deal_initial_cards(self) -> None:
        for _ in range(constants.INITIAL_TRAIN_CARDS):
            for player in self.players:
                player.train_deck.append(self.train_cards_deck.take_close_card())

        for player in self.players:
            # For the current local-PC prototype players keep all initial tickets;
            # this satisfies the rule requiring at least two kept tickets.
            player.route_deck.extend(
                self.destination_tickets_deck.draw_tickets(constants.INITIAL_DESTINATION_TICKETS)
            )

    def _activate_current_player(self) -> None:
        for player in self.players:
            player.Status = PlayerStatus.NotActive
        if not self.game_over:
            self.current_player.Status = PlayerStatus.Active

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def game_over(self) -> bool:
        return self.phase == TurnPhase.GAME_OVER

    def train_card_counts(self, player: Player | None = None) -> Counter:
        return Counter((player or self.current_player).train_deck)

    def open_train_cards(self) -> list[TrainCardType]:
        return self.train_cards_deck.get_open_cards()

    def route_points_for_length(self, length: int) -> int:
        return ROUTE_POINTS_BY_LENGTH.get(length, 15 + max(0, length - 6) * 5)

    # ------------------------------------------------------------------
    # Layout model: all rectangles are unscaled design-pixel rectangles.

    def train_card_button_states(self) -> list[CardButtonState]:
        card_w, card_h = constants.TRAIN_CARD_SIZE_PIXELS
        card_w = card_w//2
        card_h = card_h//2
        gap = 2
        total_width = len(TRAIN_CARD_BUTTON_ORDER) * card_w + (len(TRAIN_CARD_BUTTON_ORDER) - 1) * gap
        start_left = (constants.SCREEN_WIDTH_IN_PIXELS - total_width) // 2
        top = constants.SCREEN_HEIGHT_IN_PIXELS - card_h - 2
        counts = self.train_card_counts()

        states: list[CardButtonState] = []
        for index, card_type in enumerate(TRAIN_CARD_BUTTON_ORDER):
            left = start_left + index * (card_w + gap)
            rect = RectPx.from_top_left(left, top, card_w, card_h)
            states.append(CardButtonState(card_type, counts[card_type], rect, card_type == self.selected_train_card_type))
        return states

    def open_train_card_states(self) -> list[OpenTrainCardState]:
        card_w, card_h = constants.TRAIN_CARD_SIZE_PIXELS
        card_w = int(card_w / 2)
        card_h = int(card_h / 2)
        gap = 2
        cards = self.open_train_cards()
        
        # Задаем базовый отступ сверху и вертикальный зазор между рядами
        top_row_1 = 14
        top_row_2 = top_row_1 + card_h + gap
        
        # Рассчитываем общую ширину по самому длинному (второму) ряду из 3-х карт
        # Даже если карт меньше 3, мы резервируем место под полноценные 3 карты для выравнивания
        max_cards_in_row = 3
        total_width = max_cards_in_row * card_w + (max_cards_in_row - 1) * gap
        
        # Левая граница для всего блока карт (выравнивание по правому краю экрана)
        start_left = constants.SCREEN_WIDTH_IN_PIXELS - total_width - 3
        
        # Сдвиг для первого ряда, чтобы карты встали ровно «между» картами второго ряда
        row_1_offset = int(card_w / 2) + int(gap / 2)
        
        states = []
        for i, card_type in enumerate(cards):
            # Первые 2 карты идут в первый ряд (индексы 0, 1)
            if i < 2:
                left = start_left + row_1_offset + i * (card_w + gap)
                top = top_row_1
            # Остальные (индексы 2, 3, 4) идут во второй ряд
            else:
                idx_in_row2 = i - 2  # Индекс внутри второго ряда (0, 1, 2)
                left = start_left + idx_in_row2 * (card_w + gap)
                top = top_row_2
                
            states.append(
                OpenTrainCardState(i, card_type, RectPx.from_top_left(left, top, card_w, card_h))
            )
            
        return states
    
    def closed_train_deck_button_rect(self) -> RectPx:
        width, height = constants.CLOSED_TRAIN_DECK_BUTTON_SIZE_PIXELS
        return RectPx.from_top_left(constants.SCREEN_WIDTH_IN_PIXELS - width - 3, 68, width, height)

    def route_card_states(self, max_visible: int = 5) -> list[RouteCardState]:
        card_w, card_h = constants.ROUTE_CARD_SIZE_PIXELS
        gap = 2
        if self.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
            tickets = self.current_player.temp_route_deck[:max_visible]
        else:
            tickets = self.current_player.route_deck[:max_visible]
        start_left = constants.MAP_TOP_LEFT_PIXELS[0] + 2
        top = 140
        states: list[RouteCardState] = []
        for index, ticket in enumerate(tickets):
            rect = RectPx.from_top_left(start_left + index * (card_w + gap), top, card_w, card_h)
            selected = index in self.destination_ticket_keep_indices if self.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS else True
            states.append(RouteCardState(index, ticket, rect, index == self.hovered_route_card_index, selected))
        return states

    def destination_deck_button_rect(self) -> RectPx:
        card_w, card_h = constants.ROUTE_CARD_SIZE_PIXELS
        return RectPx.from_top_left(constants.SCREEN_WIDTH_IN_PIXELS - card_w - 3, 92, card_w, card_h)

    def player_plate_states(self) -> list[PlayerPlateState]:
        plate_w, plate_h = constants.PLAYER_PLATE_SIZE_PIXELS
        states: list[PlayerPlateState] = []
        for index in range(constants.MAX_PLAYERS):
            rect = RectPx.from_top_left(4, 58 + index * 25, plate_w, plate_h)
            if index < len(self.players):
                player = self.players[index]
                states.append(
                    PlayerPlateState(
                        player.ID,
                        rect,
                        index == self.current_player_index and not self.game_over,
                        True,
                        player.remaining_train_chips,
                        player.points,
                        player.chip_color,
                    )
                )
            else:
                states.append(PlayerPlateState(index + 1, rect, False, False))
        return states

    def current_player_chip_counter_rect(self) -> RectPx:
        return RectPx.from_top_left(300, 190, 24, 14)

    def current_player_score_counter_rect(self) -> RectPx:
        return RectPx.from_top_left(273, 186, 28, 14)

    # ------------------------------------------------------------------
    # Hit testing helpers for controller.

    def set_hover_from_design_point(self, x: float, y: float, is_route_card_visible:bool) -> None:
        self.hovered_route_card_index = None
        if is_route_card_visible:
            for state in self.route_card_states():
                if state.rect.contains(x, y):
                    self.hovered_route_card_index = state.index
                    break

        self.hovered_track_id = None
        hit_track = self.track_at_design_point(x, y)
        if hit_track:
            self.hovered_track_id = hit_track.id

    def route_card_at_design_point(self, x: float, y: float) -> RouteCardState | None:
        for state in self.route_card_states():
            if state.rect.contains(x, y):
                return state
        return None

    def hand_card_at_design_point(self, x: float, y: float) -> CardButtonState | None:
        for state in self.train_card_button_states():
            if state.rect.contains(x, y):
                return state
        return None

    def open_card_at_design_point(self, x: float, y: float) -> OpenTrainCardState | None:
        for state in self.open_train_card_states():
            if state.rect.contains(x, y):
                return state
        return None

    def track_at_design_point(self, x: float, y: float) -> RouteTrack | None:
        for track in self.tracks:
            for chip in track.chips:
                if chip.rect.contains(x, y):
                    return track
        return None

    def hovered_destinations(self) -> tuple[Destination, Destination] | None:
        if self.hovered_route_card_index is None:
            return None
        tickets = self.current_player.temp_route_deck if self.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS else self.current_player.route_deck
        if 0 <= self.hovered_route_card_index < len(tickets):
            ticket = tickets[self.hovered_route_card_index]
            return ticket.start, ticket.finish
        return None

    # ------------------------------------------------------------------
    # Turn actions.

    def select_train_card_type(self, card_type: TrainCardType) -> ActionResult:
        if self.game_over:
            return ActionResult(False, "Игра завершена")
        self.selected_train_card_type = card_type
        self.last_message = f"COLOR CHOSEN: {card_type.name}"
        return ActionResult(True, self.last_message)

    def take_closed_train_card(self) -> ActionResult:
        if self.phase not in (TurnPhase.WAITING_FOR_ACTION, TurnPhase.TOOK_FIRST_TRAIN_CARD):
            return ActionResult(False, "Сейчас нельзя брать карты поездов")
        try:
            card = self.train_cards_deck.take_close_card()
        except RuntimeError:
            return ActionResult(False, "Колода поездов пуста")

        self.current_player.train_deck.append(card)
        self.train_cards_taken_this_turn += 1
        self.last_message = f"PLAYER {self.current_player.ID} TOOK CARD FROM CLOSED DECK"

        if self.train_cards_taken_this_turn >= 2:
            self.end_turn()
            return ActionResult(True, self.last_message, turn_ended=True)

        self.phase = TurnPhase.TOOK_FIRST_TRAIN_CARD
        return ActionResult(True, self.last_message)

    def take_open_train_card(self, index: int) -> ActionResult:
        if self.phase not in (TurnPhase.WAITING_FOR_ACTION, TurnPhase.TOOK_FIRST_TRAIN_CARD):
            return ActionResult(False, "Сейчас нельзя брать карты поездов")

        open_cards = self.open_train_cards()
        if not 0 <= index < len(open_cards):
            return ActionResult(False, "Нет открытой карты с таким индексом")

        if self.train_cards_taken_this_turn == 1 and open_cards[index] == TrainCardType.LOCOMOTIVE:
            return ActionResult(False, "Локомотив нельзя взять второй открытой картой")

        card = self.train_cards_deck.take_open_card(index)
        self.current_player.train_deck.append(card)
        self.train_cards_taken_this_turn += 1
        self.last_message = f"PLAYER {self.current_player.ID} TOOK {card.name} OPEN CARD"

        if card == TrainCardType.LOCOMOTIVE or self.train_cards_taken_this_turn >= 2:
            self.end_turn()
            return ActionResult(True, self.last_message, turn_ended=True)

        self.phase = TurnPhase.TOOK_FIRST_TRAIN_CARD
        return ActionResult(True, self.last_message)

    def draw_destination_tickets(self) -> ActionResult:
        if self.phase != TurnPhase.WAITING_FOR_ACTION:
            return ActionResult(False, "Сейчас нельзя выбирать новые маршруты")
        drawn = self.destination_tickets_deck.draw_tickets(constants.DRAW_DESTINATION_TICKETS)
        if not drawn:
            return ActionResult(False, "Колода маршрутов пуста")
        self.current_player.temp_route_deck = drawn
        self.destination_ticket_keep_indices = set(range(len(drawn)))
        self.phase = TurnPhase.CHOOSING_DESTINATION_TICKETS
        self.last_message = f"PLAYER {self.current_player.ID} TOOK {len(drawn)} DESTINATION"
        return ActionResult(True, self.last_message)

    def keep_drawn_destination_tickets(self, keep_indices: Iterable[int]) -> ActionResult:
        if self.phase != TurnPhase.CHOOSING_DESTINATION_TICKETS:
            return ActionResult(False, "Нет маршрутов для выбора")

        offer = list(self.current_player.temp_route_deck)
        keep_set = {index for index in keep_indices if 0 <= index < len(offer)}
        if len(keep_set) < 1:
            return ActionResult(False, "Нужно оставить хотя бы один маршрут")

        kept = [ticket for index, ticket in enumerate(offer) if index in keep_set]
        returned = [ticket for index, ticket in enumerate(offer) if index not in keep_set]
        self.current_player.route_deck.extend(kept)
        self.current_player.temp_route_deck.clear()
        self.destination_ticket_keep_indices.clear()
        self.destination_tickets_deck.return_tickets(*returned)
        self.last_message = f"PLAYER {self.current_player.ID} KEPT DESTINATIONS: {len(kept)}"
        self.end_turn()
        return ActionResult(True, self.last_message, turn_ended=True)

    def auto_keep_all_drawn_destination_tickets(self) -> ActionResult:
        if self.phase != TurnPhase.CHOOSING_DESTINATION_TICKETS:
            result = self.draw_destination_tickets()
            if not result.success:
                return result
        return self.keep_drawn_destination_tickets(range(len(self.current_player.temp_route_deck)))

    def toggle_drawn_destination_ticket(self, index: int) -> ActionResult:
        if self.phase != TurnPhase.CHOOSING_DESTINATION_TICKETS:
            return ActionResult(False, "Сейчас не выбираются маршруты")
        if not 0 <= index < len(self.current_player.temp_route_deck):
            return ActionResult(False, "Маршрут не найден")
        if index in self.destination_ticket_keep_indices:
            if len(self.destination_ticket_keep_indices) <= 1:
                return ActionResult(False, "Нужно оставить хотя бы один маршрут")
            self.destination_ticket_keep_indices.remove(index)
        else:
            self.destination_ticket_keep_indices.add(index)
        self.last_message = f"DESTINATIONS CHOSEN: {len(self.destination_ticket_keep_indices)}"
        return ActionResult(True, self.last_message)

    def confirm_drawn_destination_tickets(self) -> ActionResult:
        return self.keep_drawn_destination_tickets(self.destination_ticket_keep_indices)

    def claim_track(self, track_id: str, preferred_card_type: TrainCardType | None = None) -> ActionResult:
        if self.phase != TurnPhase.WAITING_FOR_ACTION:
            return ActionResult(False, "Перегон можно пройти только до другого действия")

        track = self.track_by_id(track_id)
        if track is None:
            return ActionResult(False, "Перегон не найден")
        if track.owner != 0:
            return ActionResult(False, "Перегон уже занят")
        if self.current_player.remaining_train_chips < track.length:
            return ActionResult(False, "Не хватает фишек поездов")
        if not self._double_track_allowed(track):
            return ActionResult(False, "Этот двойной перегон уже недоступен")

        payment = self.best_payment_for_track(track, preferred_card_type)
        if payment is None:
            return ActionResult(False, "Не хватает карт нужного цвета")
        normal_count, normal_type, locomotive_count = payment

        self._spend_train_cards(normal_count, normal_type, locomotive_count)
        discard_normal_type = normal_type if normal_count > 0 else TrainCardType.WHITE
        self.train_cards_deck.discard_cards(normal_count, discard_normal_type, locomotive_count)

        track.owner = self.current_player.ID
        self.current_player.remaining_train_chips -= track.length
        self.current_player.points += self.route_points_for_length(track.length)
        self.selected_train_card_type = None
        self.last_message = f"PLAYER {self.current_player.ID} BUILT {track.station1.name}-{track.station2.name}"
        self.end_turn()
        return ActionResult(True, self.last_message, turn_ended=True)

    def track_by_id(self, track_id: str) -> RouteTrack | None:
        return next((track for track in self.tracks if track.id == track_id), None)

    def _double_track_allowed(self, track: RouteTrack) -> bool:
        if not track.double_group:
            return True
        group_tracks = [candidate for candidate in self.tracks if candidate.double_group == track.double_group and candidate is not track]

        # The same player can never take both parallel tracks.
        if any(candidate.owner == self.current_player.ID for candidate in group_tracks):
            return False

        # In 2-3 player games, only one route from a double track pair may be used.
        if self.number_of_players < 4 and any(candidate.owner != 0 for candidate in group_tracks):
            return False

        return True

    def best_payment_for_track(
        self,
        track: RouteTrack | str,
        preferred_card_type: TrainCardType | None = None,
    ) -> tuple[int, TrainCardType, int] | None:
        if isinstance(track, str):
            found = self.track_by_id(track)
            if found is None:
                return None
            track = found

        counts = self.train_card_counts()
        locomotives = counts[TrainCardType.LOCOMOTIVE]
        allowed_colors: list[TrainCardType]

        if track.color is not None:
            allowed_colors = [track.color]
        elif preferred_card_type and preferred_card_type != TrainCardType.LOCOMOTIVE:
            allowed_colors = [preferred_card_type]
        else:
            allowed_colors = [card for card in TRAIN_CARD_BUTTON_ORDER if card != TrainCardType.LOCOMOTIVE]

        best: tuple[int, TrainCardType, int] | None = None
        for card_type in allowed_colors:
            normal_available = counts[card_type]
            normal_count = min(normal_available, track.length)
            locomotive_count = track.length - normal_count
            if locomotive_count <= locomotives:
                candidate = (normal_count, card_type, locomotive_count)
                if best is None or candidate[0] > best[0]:
                    best = candidate

        if best is None and preferred_card_type == TrainCardType.LOCOMOTIVE and locomotives >= track.length:
            best = (0, TrainCardType.WHITE, track.length)

        return best

    def _spend_train_cards(self, normal_count: int, normal_type: TrainCardType, locomotive_count: int) -> None:
        for _ in range(normal_count):
            self.current_player.train_deck.remove(normal_type)
        for _ in range(locomotive_count):
            self.current_player.train_deck.remove(TrainCardType.LOCOMOTIVE)

    def end_turn(self) -> None:
        if self.game_over:
            return

        self.current_player.Status = PlayerStatus.NotActive
        self.train_cards_taken_this_turn = 0
        self.selected_train_card_type = None
        self.hovered_route_card_index = None
        self.hovered_track_id = None

        started_final_now = False
        if self.final_turns_remaining is None and self.current_player.remaining_train_chips <= 2:
            self.final_turns_remaining = len(self.players)
            started_final_now = True
            self.last_message = f"FINAL TURN HAD STARTED: PLAYER {self.current_player.ID} HAS 2 OR LESS TRAIN CHIPS"
        elif self.final_turns_remaining is not None:
            self.final_turns_remaining -= 1
            if self.final_turns_remaining <= 0:
                self.apply_final_scoring()
                self.phase = TurnPhase.GAME_OVER
                self._activate_current_player()
                return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.phase = TurnPhase.WAITING_FOR_ACTION
        self._activate_current_player()

        if started_final_now:
            # Keep the informational message after the player index advances.
            return

    # ------------------------------------------------------------------
    # Final scoring and route graph logic.

    def player_claimed_tracks(self, player_id: int) -> list[RouteTrack]:
        return [track for track in self.tracks if track.owner == player_id]

    def has_connected_destinations(self, player_id: int, start: Destination, finish: Destination) -> bool:
        if start == finish:
            return True

        graph: dict[Destination, set[Destination]] = defaultdict(set)
        for track in self.player_claimed_tracks(player_id):
            graph[track.station1].add(track.station2)
            graph[track.station2].add(track.station1)

        visited = {start}
        queue = deque([start])
        while queue:
            city = queue.popleft()
            for neighbor in graph[city]:
                if neighbor == finish:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def completed_ticket_count(self, player_id: int) -> int:
        player = self.players[player_id - 1]
        return sum(
            1
            for ticket in player.route_deck
            if self.has_connected_destinations(player_id, ticket.start, ticket.finish)
        )

    def longest_continuous_road(self, player_id: int) -> int:
        claimed = self.player_claimed_tracks(player_id)
        if not claimed:
            return 0

        graph: dict[Destination, list[tuple[Destination, int, str]]] = defaultdict(list)
        for track in claimed:
            graph[track.station1].append((track.station2, track.length, track.id))
            graph[track.station2].append((track.station1, track.length, track.id))

        def dfs(city: Destination, used_track_ids: set[str]) -> int:
            best = 0
            for neighbor, length, track_id in graph[city]:
                if track_id in used_track_ids:
                    continue
                used_track_ids.add(track_id)
                best = max(best, length + dfs(neighbor, used_track_ids))
                used_track_ids.remove(track_id)
            return best

        return max(dfs(city, set()) for city in graph)

    def apply_final_scoring(self) -> FinalScoreSummary:
        if self.final_scores_applied:
            return self.final_score_summary

        completed: dict[int, int] = {}
        longest: dict[int, int] = {}

        for player in self.players:
            completed_count = 0
            for ticket in player.route_deck:
                if self.has_connected_destinations(player.ID, ticket.start, ticket.finish):
                    player.points += ticket.price
                    completed_count += 1
                else:
                    player.points -= ticket.price
            completed[player.ID] = completed_count
            longest[player.ID] = self.longest_continuous_road(player.ID)

        max_longest = max(longest.values(), default=0)
        bonus_player_ids = [player_id for player_id, value in longest.items() if value == max_longest and value > 0]
        for player_id in bonus_player_ids:
            self.players[player_id - 1].points += 10

        self.final_score_summary = FinalScoreSummary(
            completed_tickets=completed,
            longest_roads=longest,
            longest_bonus_player_ids=bonus_player_ids,
            winner_ids=self._calculate_winners(completed, longest),
        )
        self.final_scores_applied = True
        return self.final_score_summary

    def _calculate_winners(self, completed: dict[int, int], longest: dict[int, int]) -> list[int]:
        best_tuple: tuple[int, int, int] | None = None
        winners: list[int] = []
        for player in self.players:
            ranking = (player.points, completed.get(player.ID, 0), longest.get(player.ID, 0))
            if best_tuple is None or ranking > best_tuple:
                best_tuple = ranking
                winners = [player.ID]
            elif ranking == best_tuple:
                winners.append(player.ID)
        return winners
