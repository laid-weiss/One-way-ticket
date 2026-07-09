import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tempfile
import unittest
from pathlib import Path

from model.game_model import GameModel, TurnPhase
from utils.board import GameType
from utils.destination_tickets import Destination, DestinationTicket, DestinationTicketType
from utils.game_settings import GameSettings, Settings
from utils.player import TRAIN_CHIP_COLOR
from utils.train_cards import TrainCardType


class TestGameModel(unittest.TestCase):
    def make_settings(self, players=2):
        colors = [TRAIN_CHIP_COLOR.RED, TRAIN_CHIP_COLOR.BLUE, TRAIN_CHIP_COLOR.GREEN, TRAIN_CHIP_COLOR.YELLOW]
        return Settings(GameType.LOCAL_GAME, players, colors[:players])

    def test_initializes_up_to_four_local_players(self):
        model = GameModel(self.make_settings(players=4), random_seed=1)

        self.assertEqual(len(model.players), 4)
        self.assertEqual(model.current_player.ID, 1)
        self.assertEqual([player.chip_color for player in model.players], [
            TRAIN_CHIP_COLOR.RED,
            TRAIN_CHIP_COLOR.BLUE,
            TRAIN_CHIP_COLOR.GREEN,
            TRAIN_CHIP_COLOR.YELLOW,
        ])
        self.assertTrue(all(len(player.train_deck) == 4 for player in model.players))
        self.assertTrue(all(len(player.route_deck) >= 2 for player in model.players))
        self.assertEqual(len(model.open_train_cards()), 5)

    def test_take_open_locomotive_first_card_ends_turn(self):
        model = GameModel(self.make_settings(), random_seed=2)
        model.train_cards_deck._MainTrainCardDeck__open_cards = [
            TrainCardType.LOCOMOTIVE,
            TrainCardType.RED,
            TrainCardType.BLUE,
            TrainCardType.GREEN,
            TrainCardType.WHITE,
        ]
        model.train_cards_deck._MainTrainCardDeck__remaining_cards = [TrainCardType.YELLOW] * 10

        result = model.take_open_train_card(0)

        self.assertTrue(result.success)
        self.assertTrue(result.turn_ended)
        self.assertIn(TrainCardType.LOCOMOTIVE, model.players[0].train_deck)
        self.assertEqual(model.current_player.ID, 2)
        self.assertEqual(model.phase, TurnPhase.WAITING_FOR_ACTION)

    def test_cannot_take_open_locomotive_as_second_card(self):
        model = GameModel(self.make_settings(), random_seed=3)
        model.train_cards_deck._MainTrainCardDeck__open_cards = [
            TrainCardType.RED,
            TrainCardType.LOCOMOTIVE,
            TrainCardType.BLUE,
            TrainCardType.GREEN,
            TrainCardType.WHITE,
        ]
        model.train_cards_deck._MainTrainCardDeck__remaining_cards = [TrainCardType.YELLOW] * 10

        first = model.take_open_train_card(0)
        second = model.take_open_train_card(1)

        self.assertTrue(first.success)
        self.assertFalse(second.success)
        self.assertEqual(model.current_player.ID, 1)
        self.assertEqual(model.phase, TurnPhase.TOOK_FIRST_TRAIN_CARD)

    def test_claim_track_spends_cards_scores_and_advances_turn(self):
        model = GameModel(self.make_settings(), random_seed=4)
        model.current_player.train_deck = [TrainCardType.YELLOW] * 3
        track = model.track_by_id("la-wa-a")

        result = model.claim_track("la-wa-a", TrainCardType.YELLOW)

        self.assertTrue(result.success)
        self.assertEqual(track.owner, 1)
        self.assertEqual(model.players[0].remaining_train_chips, 42)
        self.assertEqual(model.players[0].points, 4)
        self.assertEqual(model.players[0].train_deck, [])
        self.assertEqual(model.train_cards_deck.discard_count(), 3)
        self.assertEqual(model.current_player.ID, 2)

    def test_double_track_is_blocked_for_two_or_three_players(self):
        model = GameModel(self.make_settings(players=2), random_seed=5)
        model.current_player.train_deck = [TrainCardType.YELLOW] * 3
        self.assertTrue(model.claim_track("la-wa-a", TrainCardType.YELLOW).success)

        model.current_player.train_deck = [TrainCardType.GREEN] * 4
        result = model.claim_track("la-wa-b", TrainCardType.GREEN)

        self.assertFalse(result.success)
        self.assertEqual(model.track_by_id("la-wa-b").owner, 0)

    def test_destination_ticket_scoring_and_longest_road_bonus(self):
        model = GameModel(self.make_settings(), random_seed=6)
        for player in model.players:
            player.route_deck.clear()
            player.points = 0

        model.players[0].route_deck = [
            DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.DC, 10),
            DestinationTicket(DestinationTicketType.SHORT, Destination.LA, Destination.WA, 5),
        ]
        model.track_by_id("la-wa-a").owner = 1
        model.track_by_id("wa-dc").owner = 1

        summary = model.apply_final_scoring()

        self.assertEqual(summary.completed_tickets[1], 2)
        self.assertIn(1, summary.longest_bonus_player_ids)
        self.assertEqual(model.players[0].points, 25)
        self.assertEqual(summary.winner_ids, [1])

    def test_drawn_destination_tickets_can_be_toggled_and_confirmed(self):
        model = GameModel(self.make_settings(), random_seed=9)
        original_count = len(model.current_player.route_deck)

        result = model.draw_destination_tickets()
        self.assertTrue(result.success)
        self.assertEqual(model.phase, TurnPhase.CHOOSING_DESTINATION_TICKETS)
        self.assertEqual(model.destination_ticket_keep_indices, set(range(len(model.current_player.temp_route_deck))))

        model.toggle_drawn_destination_ticket(0)
        kept_count = len(model.destination_ticket_keep_indices)
        result = model.confirm_drawn_destination_tickets()

        self.assertTrue(result.success)
        self.assertEqual(len(model.players[0].route_deck), original_count + kept_count)
        self.assertEqual(model.current_player.ID, 2)
        self.assertEqual(model.phase, TurnPhase.WAITING_FOR_ACTION)

    def test_final_circle_starts_when_player_has_two_or_fewer_trains(self):
        model = GameModel(self.make_settings(players=2), random_seed=8)
        for player in model.players:
            player.route_deck.clear()
        model.current_player.remaining_train_chips = 2

        model.end_turn()
        self.assertEqual(model.final_turns_remaining, 2)
        self.assertEqual(model.current_player.ID, 2)

        model.end_turn()
        self.assertEqual(model.final_turns_remaining, 1)
        self.assertEqual(model.current_player.ID, 1)

        model.end_turn()
        self.assertEqual(model.phase, TurnPhase.GAME_OVER)
        self.assertTrue(model.final_scores_applied)

    def test_route_card_hover_exposes_destinations_for_highlight(self):
        model = GameModel(self.make_settings(), random_seed=7)
        state = model.route_card_states()[0]

        model.set_hover_from_design_point(state.rect.center_x, state.rect.center_y)

        self.assertEqual(model.hovered_destinations(), (state.ticket.start, state.ticket.finish))

    def test_settings_are_serialized_and_deserialized(self):
        settings = GameSettings(self.make_settings(players=3))
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "settings.json"
            settings.save(path)
            loaded = GameSettings.load(path)

        self.assertEqual(loaded.get_settings.game_type, GameType.LOCAL_GAME)
        self.assertEqual(loaded.get_settings.number_of_players, 3)
        self.assertEqual(loaded.get_settings.chip_colors, [
            TRAIN_CHIP_COLOR.RED,
            TRAIN_CHIP_COLOR.BLUE,
            TRAIN_CHIP_COLOR.GREEN,
        ])


if __name__ == "__main__":
    unittest.main()
