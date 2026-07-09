from __future__ import annotations

from pathlib import Path

import arcade
from PIL import Image, ImageSequence

from ..model.game_model import CITY_POINTS_TOP_LEFT, GameModel, RectPx, TRAIN_CARD_BUTTON_ORDER, TurnPhase
from ..utils import constants
from ..utils.player import TRAIN_CHIP_COLOR
from ..utils.train_cards import TrainCardType


class GameTableView:
    """Drawing-only view for the main scene. It reads state from GameModel."""

    def __init__(self, model: GameModel):
        self.model = model
        arcade.load_font(str(constants.MAIN_FONT_PATH))
        self.font_name = constants.MAIN_FONT_NAME

        self.frame_texture = arcade.load_texture(constants.HOME_DIR / "assets" / "game_table" / "frame.png")
        self.map_texture = arcade.load_texture(constants.HOME_DIR / "assets" / "map" / "map.png")
        self.route_card_texture = arcade.load_texture(constants.HOME_DIR / "assets" / "route_cards" / "card.png")
        self.closed_deck_button = [
            arcade.load_texture(constants.HOME_DIR / "assets" / "elements" / "take_card_no_pressed.png"),
            arcade.load_texture(constants.HOME_DIR / "assets" / "elements" / "take_card_pressed.png"),
        ]

        train_cards_dir = constants.HOME_DIR / "assets" / "train_cards"
        self.train_card_textures = {
            TrainCardType.WHITE: arcade.load_texture(train_cards_dir / "card_white.png"),
            TrainCardType.BLACK: arcade.load_texture(train_cards_dir / "card_black.png"),
            TrainCardType.YELLOW: arcade.load_texture(train_cards_dir / "card_yellow.png"),
            TrainCardType.GREEN: arcade.load_texture(train_cards_dir / "card_green.png"),
            TrainCardType.BLUE: arcade.load_texture(train_cards_dir / "card_blue.png"),
            # There is no card_red.png in the current asset pack; brown is the closest placeholder.
            TrainCardType.RED: arcade.load_texture(train_cards_dir / "card_brown.png"),
            TrainCardType.ORANGE: arcade.load_texture(train_cards_dir / "card_orange.png"),
            TrainCardType.PURPLE: arcade.load_texture(train_cards_dir / "card_purple.png"),
            TrainCardType.LOCOMOTIVE: arcade.load_texture(train_cards_dir / "locomotive.png"),
        }

        chips_dir = constants.HOME_DIR / "assets" / "train_chips"
        self.chip_frames = {
            TRAIN_CHIP_COLOR.RED: self._load_gif_frames(chips_dir / "red_chip.gif"),
            TRAIN_CHIP_COLOR.BLUE: self._load_gif_frames(chips_dir / "blue_chip.gif"),
            TRAIN_CHIP_COLOR.GREEN: self._load_gif_frames(chips_dir / "green_chip.gif"),
            TRAIN_CHIP_COLOR.YELLOW: self._load_gif_frames(chips_dir / "yellow_chip.gif"),
            TRAIN_CHIP_COLOR.BLACK: self._load_gif_frames(chips_dir / "black_chip.gif"),
        }

        self.player_color_map = {
            TRAIN_CHIP_COLOR.RED: arcade.color.CRIMSON,
            TRAIN_CHIP_COLOR.BLUE: arcade.color.ROYAL_BLUE,
            TRAIN_CHIP_COLOR.GREEN: arcade.color.FOREST_GREEN,
            TRAIN_CHIP_COLOR.YELLOW: arcade.color.GOLD,
            TRAIN_CHIP_COLOR.BLACK: arcade.color.BLACK,
        }

    def _load_gif_frames(self, path: Path):
        frames = []
        with Image.open(path) as image:
            for frame_index, frame in enumerate(ImageSequence.Iterator(image)):
                pil_frame = frame.convert("RGBA").copy()
                frames.append(arcade.Texture(pil_frame, hash=f"{path.name}:{frame_index}"))
        if not frames:
            frames.append(arcade.load_texture(path))
        return frames

    def _scaled_rect(self, rect: RectPx):
        return arcade.LBWH(
            rect.left * constants.PIXEL_SIZE,
            rect.bottom * constants.PIXEL_SIZE,
            rect.width * constants.PIXEL_SIZE,
            rect.height * constants.PIXEL_SIZE,
        )

    def _draw_texture_in_rect(self, texture, rect: RectPx):
        arcade.draw_texture_rect(texture, self._scaled_rect(rect))

    def _draw_text(
        self,
        text: str,
        x: float,
        y: float,
        color=arcade.color.WHITE,
        font_size: int = 5,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
    ):
        arcade.draw_text(
            text,
            x * constants.PIXEL_SIZE,
            y * constants.PIXEL_SIZE,
            color,
            font_size=font_size * constants.PIXEL_SIZE,
            font_name=self.font_name,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
        )

    def draw(self):
        self._draw_background()
        self._draw_city_highlights()
        self._draw_claimed_wagons()
        self._draw_player_plates()
        self._draw_open_train_cards()
        self._draw_destination_deck_button()
        self._draw_route_cards()
        self._draw_train_card_buttons()
        self._draw_current_player_counters()
        self._draw_status_text()

    def _draw_background(self):
        frame_rect = RectPx(0, 0, constants.SCREEN_WIDTH_IN_PIXELS, constants.SCREEN_HEIGHT_IN_PIXELS)
        self._draw_texture_in_rect(self.frame_texture, frame_rect)

        map_left, map_top = constants.MAP_TOP_LEFT_PIXELS
        map_width, map_height = constants.MAP_SIZE_PIXELS
        map_rect = RectPx.from_top_left(map_left, map_top, map_width, map_height)
        self._draw_texture_in_rect(self.map_texture, map_rect)

    def _draw_city_highlights(self):
        destinations = self.model.hovered_destinations()
        if destinations is None:
            return

        map_left, map_top = constants.MAP_TOP_LEFT_PIXELS
        for destination in destinations:
            city_point = CITY_POINTS_TOP_LEFT.get(destination)
            if city_point is None:
                continue
            design_x = map_left + city_point[0]
            design_y = constants.SCREEN_HEIGHT_IN_PIXELS - (map_top + city_point[1])
            arcade.draw_circle_filled(
                design_x * constants.PIXEL_SIZE,
                design_y * constants.PIXEL_SIZE,
                5 * constants.PIXEL_SIZE,
                (255, 230, 80, 190),
            )
            arcade.draw_circle_outline(
                design_x * constants.PIXEL_SIZE,
                design_y * constants.PIXEL_SIZE,
                7 * constants.PIXEL_SIZE,
                arcade.color.WHITE,
                1 * constants.PIXEL_SIZE,
            )

    def _draw_claimed_wagons(self):
        for track in self.model.tracks:
            owner_id = track.owner
            if owner_id == 0:
                if self.model.hovered_track_id == track.id:
                    for chip in track.chips:
                        arcade.draw_rect_outline(
                            self._scaled_rect(chip.rect),
                            (255, 255, 255, 120),
                            border_width=max(1, constants.PIXEL_SIZE),
                        )
                continue

            player = self.model.players[owner_id - 1]
            frames = self.chip_frames[player.chip_color]
            for chip in track.chips:
                texture = frames[chip.frame_index % len(frames)]
                self._draw_texture_in_rect(texture, chip.rect)

    def _draw_player_plates(self):
        for plate in self.model.player_plate_states():
            if not plate.is_present:
                self._draw_text("--", plate.rect.center_x, plate.rect.center_y - 2, arcade.color.GRAY, 5, "center", "center")
                continue

            text_color = arcade.color.WHITE
            color = self.player_color_map.get(plate.chip_color, arcade.color.WHITE)
            arcade.draw_rect_outline(self._scaled_rect(plate.rect), color, border_width=max(1, constants.PIXEL_SIZE))

            if plate.is_active:
                self._draw_turn_arrow(plate.rect)

            self._draw_text(f"P{plate.player_id}", plate.rect.left + 4, plate.rect.bottom + 14, text_color, 4)
            self._draw_text(f"T:{plate.remaining_train_chips:02}", plate.rect.left + 17, plate.rect.bottom + 14, text_color, 4)
            self._draw_text(f"P:{plate.points:02}", plate.rect.left + 17, plate.rect.bottom + 5, text_color, 4)

    def _draw_turn_arrow(self, rect: RectPx):
        x = (rect.left - 3) * constants.PIXEL_SIZE
        y = rect.center_y * constants.PIXEL_SIZE
        size = 5 * constants.PIXEL_SIZE
        arcade.draw_triangle_filled(
            x,
            y,
            x - size,
            y + size,
            x - size,
            y - size,
            arcade.color.WHITE,
        )

    def _draw_open_train_cards(self):
        for state in self.model.open_train_card_states():
            self._draw_texture_in_rect(self.train_card_textures[state.card_type], state.rect)

        button_rect = self.model.closed_train_deck_button_rect()
        self._draw_texture_in_rect(self.closed_deck_button[0], button_rect)

    def _draw_destination_deck_button(self):
        rect = self.model.destination_deck_button_rect()
        self._draw_texture_in_rect(self.route_card_texture, rect)
        label = "KEEP" if self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS else "NEW"
        self._draw_text(label, rect.center_x, rect.bottom + 28, arcade.color.BLACK, 4, "center", "center")
        self._draw_text("ROUT", rect.center_x, rect.bottom + 18, arcade.color.BLACK, 4, "center", "center")

    def _draw_route_cards(self):
        for state in self.model.route_card_states():
            self._draw_texture_in_rect(self.route_card_texture, state.rect)
            ticket = state.ticket
            self._draw_text(ticket.start.name, state.rect.center_x, state.rect.bottom + 33, arcade.color.BLACK, 5, "center", "center")
            self._draw_text(ticket.finish.name, state.rect.center_x, state.rect.bottom + 21, arcade.color.BLACK, 5, "center", "center")
            self._draw_text(str(ticket.price), state.rect.center_x, state.rect.bottom + 8, arcade.color.BLACK, 5, "center", "center")
            if self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
                outline_color = (50, 220, 50) if state.selected else (150, 20, 20)
                arcade.draw_rect_outline(self._scaled_rect(state.rect), outline_color, border_width=max(1, constants.PIXEL_SIZE))
            if state.hovered:
                arcade.draw_rect_outline(self._scaled_rect(state.rect), arcade.color.WHITE, border_width=max(1, constants.PIXEL_SIZE))

    def _draw_train_card_buttons(self):
        for state in self.model.train_card_button_states():
            self._draw_texture_in_rect(self.train_card_textures[state.card_type], state.rect)
            counter_color = arcade.color.BLACK if state.card_type in (TrainCardType.WHITE, TrainCardType.YELLOW) else arcade.color.WHITE
            if state.card_type == TrainCardType.LOCOMOTIVE:
                counter_color = arcade.color.WHITE
            self._draw_text(str(state.count), state.rect.center_x, state.rect.bottom + 7, counter_color, 7, "center", "center")
            if state.selected:
                arcade.draw_rect_outline(self._scaled_rect(state.rect), arcade.color.WHITE, border_width=max(1, 2 * constants.PIXEL_SIZE))

    def _draw_current_player_counters(self):
        chips_rect = self.model.current_player_chip_counter_rect()
        score_rect = self.model.current_player_score_counter_rect()
        player = self.model.current_player
        self._draw_text(str(player.remaining_train_chips), chips_rect.center_x, chips_rect.center_y, arcade.color.WHITE, 7, "center", "center")
        self._draw_text(str(player.points), score_rect.center_x, score_rect.center_y, arcade.color.WHITE, 7, "center", "center")

    def _draw_status_text(self):
        if self.model.phase == TurnPhase.GAME_OVER:
            winners = ",".join(f"P{player_id}" for player_id in self.model.final_score_summary.winner_ids)
            message = f"GAME OVER  WIN: {winners}"
        elif self.model.phase == TurnPhase.CHOOSING_DESTINATION_TICKETS:
            message = f"P{self.model.current_player.ID}: SELECT ROUTES, CLICK KEEP"
        else:
            message = f"P{self.model.current_player.ID} TURN"
            if self.model.final_turns_remaining is not None:
                message += f"  FINAL:{self.model.final_turns_remaining}"
        if self.model.last_message:
            message += f"  {self.model.last_message[:32]}"
        self._draw_text(message, 62, 214, arcade.color.WHITE, 4)


# Backward-compatible name for older imports.
GameView = GameTableView
