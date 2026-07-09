import arcade
from ..utils.board import GameType
from ..utils.game_settings import GameSettings


class SettingsController:
    def __init__(self, model, on_back_callback, settings : GameSettings):
        self.model = model
        self.on_back_callback = on_back_callback
        self.settings = settings
        self.row_gap = 60

    def get_row_y(self, window_height, row_index):
        return window_height - 150 - (row_index * self.row_gap)

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
            
        window_height = arcade.get_window().height
        center_x = arcade.get_window().width / 2
        
        # Row 0: Game Mode
        row0_y = self.get_row_y(window_height, 0)
        clicked_mode = self.check_text_radio_clicks(x, y, center_x, row0_y, self.model.mode_options)
        if clicked_mode:
            self.model.game_mode = clicked_mode
            return
            
        # Dynamic Rows based on Game Mode
        if self.model.game_mode == GameType.BOT_GAME:
            row1_y = self.get_row_y(window_height, 1)
            row2_y = self.get_row_y(window_height, 2)
            
            # Difficulty
            clicked_diff = self.check_text_radio_clicks(x, y, center_x, row1_y, self.model.difficulty_options)
            if clicked_diff:
                self.model.bot_difficulty = clicked_diff
                return
                
            # P1 Color
            self.check_color_radio_clicks(x, y, center_x, row2_y, 0)
                
        else:
            row1_y = self.get_row_y(window_height, 1)
            
            # Number of Players
            clicked_players = self.check_text_radio_clicks(x, y, center_x, row1_y, self.model.player_options)
            if clicked_players:
                self.model.num_players = clicked_players
                return
                
            # Player Colors
            for i in range(self.model.num_players):
                player_key = i
                row_y = self.get_row_y(window_height, i + 2)
                if self.check_color_radio_clicks(x, y, center_x, row_y, player_key):
                    return 
                
        # Back Button Check
        if self.is_hit(x, y, center_x, 80, 200, 50):
            self.settings.update_settings(self.model.game_mode, 
                                          self.model.num_players, 
                                          self.model.player_colors[:self.model.num_players])
            self.settings.save()
            self.on_back_callback()

    def check_text_radio_clicks(self, mouse_x, mouse_y, center_x, row_y, options):
        """Returns the selected option if clicked, or None."""
        start_x = center_x - 120
        spacing = 100
        
        for i, option in enumerate(options):
            opt_x = start_x + (i * spacing)
            
            # Hitbox spanning from the left of the circle to the end of typical text
            if (opt_x - 15 < mouse_x < opt_x + 80 and 
                row_y - 15 < mouse_y < row_y + 15):
                return option
        return None

    def check_color_radio_clicks(self, mouse_x, mouse_y, center_x, row_y, player_key):
        """Updates the model and returns True if a color circle was clicked."""
        start_x = center_x - 120
        spacing = 50
        hit_radius = 20 
        
        for i in self.model.color_options:
            btn_x = start_x + (i.value * spacing)
            
            if (btn_x - hit_radius < mouse_x < btn_x + hit_radius and 
                row_y - hit_radius < mouse_y < row_y + hit_radius):
                
                self.model.player_colors[player_key] = i
                return True 
                
        return False 

    def is_hit(self, mouse_x, mouse_y, center_x, center_y, width, height):
        return (center_x - width/2 < mouse_x < center_x + width/2 and 
                center_y - height/2 < mouse_y < center_y + height/2)