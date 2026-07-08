import arcade
from os import path
from pathlib import Path
from ..utils import constants

class MainMenuView:
    def __init__(self, model, container):
        self.model = model
        self.container = container
        
        self.background = arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_nobutton.png')
        self.button_start = [arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_play_no_pressed.png'), 
                             arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_play_pressed.png')]
        self.button_settings = [arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_settings_no_pressed.png'), 
                             arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_settings_pressed.png')]
        self.button_exit = [arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_exit_no_pressed.png'), 
                             arcade.load_texture(constants.HOME_DIR/'assets'/'menu'/'menu_with_good_font'/'menu_exit_pressed.png')]

    def draw(self):
        
        arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        

        # Draw the buttons based on model state
        for option in self.model.options:
            
            
            
            
            if option["id"] == "start":
                current_button_texture = self.button_start[not option["is_hovered"]]
            elif option["id"] == "settings":
                current_button_texture = self.button_settings[not option["is_hovered"]]
            else:
                current_button_texture = self.button_exit[not option["is_hovered"]]

            arcade.draw_texture_rect(current_button_texture, arcade.LBWH(left=option["x"], 
                                                                         bottom=option["y"], 
                                                                         width=option["width"], 
                                                                         height=option["height"]))