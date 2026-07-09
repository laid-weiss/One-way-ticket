import arcade
from ..utils import game_settings
from ..utils.board import DifficultyLevel, TrainChipColors, DifficultyLevelToStr, GameTypeToStr
from ..utils import constants

class SettingsGraphicsView:
    def __init__(self, model):
        self.model = model
        self.row_gap = 60

        self.color_map = {
            TrainChipColors.RED: arcade.color.CRIMSON,
            TrainChipColors.BLUE: arcade.color.ROYAL_BLUE,
            TrainChipColors.GREEN: arcade.color.FOREST_GREEN,
            TrainChipColors.YELLOW: arcade.color.GOLD,
            TrainChipColors.BLACK: arcade.color.BLACK
        }

    def get_row_y(self, window_height, row_index):
        return window_height - 150 - (row_index * self.row_gap)

    def draw(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        
        window_width = arcade.get_window().width
        window_height = arcade.get_window().height
        center_x = window_width / 2
        
        # Title
        arcade.draw_text("SETTINGS", center_x, window_height - 80,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        
        # Row 0: Game Mode Radio Buttons
        row0_y = self.get_row_y(window_height, 0)
        self.draw_text_radio_row(center_x, row0_y, "Mode:", self.model.mode_options, self.model.game_mode)
        
        # Dynamic Rows
        if self.model.game_mode == game_settings.GameType.BOT_GAME:
            row1_y = self.get_row_y(window_height, 1)
            row2_y = self.get_row_y(window_height, 2)
            
            # Bot Difficulty & Color
            self.draw_text_radio_row(center_x, row1_y, "Difficulty:", self.model.difficulty_options, self.model.bot_difficulty)
            self.draw_color_radio_row(center_x, row2_y, "Your Color:", self.model.player_colors[0])
        else:
            row1_y = self.get_row_y(window_height, 1)
            
            # Number of Players
            self.draw_text_radio_row(center_x, row1_y, "Players:", self.model.player_options, self.model.num_players)
            
            # Draw color radio rows for active players
            for i in range(self.model.num_players):
                player_key = i
                row_y = self.get_row_y(window_height, i + 2)
                self.draw_color_radio_row(center_x, row_y, f"Player {i+1}:", self.model.player_colors[player_key])
            
        # Back Button
        arcade.draw_rect_filled(arcade.XYWH(center_x, 80, 200, 50), arcade.color.DARK_RED)
        arcade.draw_text("BACK", center_x, 70, arcade.color.WHITE, font_size=20, anchor_x="center")

    def draw_text_radio_row(self, center_x, y, label, options, selected_option):
        """Draws standard radio buttons (empty circle / filled circle) with text labels."""
        arcade.draw_text(label, center_x - 160, y - 6, arcade.color.WHITE, font_size=18, anchor_x="right")
        
        start_x = center_x - 120
        spacing = 120 
        
        for i, option in enumerate(options):
            opt_x = start_x + (i * spacing)
            
            # Draw the outer ring
            arcade.draw_circle_outline(opt_x, y, 10, arcade.color.WHITE, 2)
            
            # Draw the filled inner circle if selected
            if option == selected_option:
                arcade.draw_circle_filled(opt_x, y, 5, arcade.color.WHITE)
                
            # Draw the option text next to the radio circle
            if (isinstance(option, DifficultyLevel)):
                arcade.draw_text(DifficultyLevelToStr[option.value], opt_x + 18, y - 6, arcade.color.WHITE, font_size=16)
            elif (isinstance(option, game_settings.GameType)):
                arcade.draw_text(GameTypeToStr[option.value], opt_x + 18, y - 6, arcade.color.WHITE, font_size=16)
            else:
                arcade.draw_text(option, opt_x + 18, y - 6, arcade.color.WHITE, font_size=16)

    def draw_color_radio_row(self, center_x, y, label, selected_color):
        """Draws colored circles for player train color selection."""
        arcade.draw_text(label, center_x - 160, y - 6, arcade.color.WHITE, font_size=18, anchor_x="right")
        
        start_x = center_x - 120
        spacing = 50
        
        for i, color_name in enumerate(self.model.color_options):
            btn_x = start_x + (i * spacing)
            color_val = self.color_map[color_name]
            
            arcade.draw_circle_filled(btn_x, y, 16, color_val)
            
            if color_name == selected_color:
                arcade.draw_circle_outline(btn_x, y, 20, arcade.color.WHITE, 3)