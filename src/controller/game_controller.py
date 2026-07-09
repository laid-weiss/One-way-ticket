import arcade

from ..model.game_model import GameModel, TurnPhase
from ..utils import constants


class GameController:
    """Local human controller. Bot/network controllers can call the same model API."""

    def __init__(self, model: GameModel, container, View):
        self.model = model
        self.container = container
        self.view = View

    def _to_design_pixels(self, x: float, y: float) -> tuple[float, float]:
        return x / constants.PIXEL_SIZE, y / constants.PIXEL_SIZE

    def on_mouse_motion(self, x, y, dx, dy):
        design_x, design_y = self._to_design_pixels(x, y)
        self.model.set_hover_from_design_point(design_x, design_y, self.view.show_route_cards[self.model.current_player_index])

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        design_x, design_y = self._to_design_pixels(x, y)

        if self.model.destination_deck_button_rect().contains(design_x, design_y):
            if self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
                self.model.confirm_drawn_destination_tickets()
            else:
                self.model.draw_destination_tickets()
                self.view.show_route_cards[self.model.current_player_index] = True
            return

        if self.model.closed_train_deck_button_rect().contains(design_x, design_y):
            self.model.take_closed_train_card()
            return

        open_card = self.model.open_card_at_design_point(design_x, design_y)
        if open_card is not None:
            self.model.take_open_train_card(open_card.index)
            return

        hand_card = self.model.hand_card_at_design_point(design_x, design_y)
        if hand_card is not None:
            self.model.select_train_card_type(hand_card.card_type)
            return

        track = self.model.track_at_design_point(design_x, design_y)
        if track is not None:
            self.model.claim_track(track.id, self.model.selected_train_card_type)
            return

        route_card = self.model.route_card_at_design_point(design_x, design_y)
        if route_card is not None:
            self.model.hovered_route_card_index = route_card.index
            if self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
                self.model.toggle_drawn_destination_ticket(route_card.index)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.container.go_back_to_menu()
        elif symbol == arcade.key.SPACE and self.model.phase != TurnPhase.GAME_OVER:
            self.model.end_turn()
        elif symbol == arcade.key.T and self.model.phase != TurnPhase.GAME_OVER:
            self.view.show_route_cards[self.model.current_player_index] = True
            self.model.draw_destination_tickets()
        elif symbol == arcade.key.S:
            self.view.show_route_cards[self.model.current_player_index] = not self.view.show_route_cards[self.model.current_player_index]
        elif symbol == arcade.key.ENTER and self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
            self.model.confirm_drawn_destination_tickets()
        elif symbol == arcade.key.F:
            self.model.apply_final_scoring()
            self.model.phase = TurnPhase.GAME_OVER
