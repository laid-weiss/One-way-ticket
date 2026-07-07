from ..utils import constants

#button: 320 x 224
#

class MainMenuModel:
    
    button_x_offset = 0
    button_start_y_offset = 0
    button_settings_y_offset = 0
    button_quit_y_offset = 0
    
    def __init__(self, container):
        
        self.container = container
        
        # Define the buttons/options for the menu
        self.options = [
            {
                "id": "start",
                "x": self.button_x_offset ,
                "y": self.button_start_y_offset,
                "width": 320*4, 
                "height": 224*4, 
                "is_hovered": False,
                "is_pressed" : False
            },
            {
                "id": "settings",
                "x": self.button_x_offset, 
                "y": self.button_settings_y_offset,
                "width": 320*4, 
                "height": 224*4, 
                "is_hovered": False,
                "is_pressed" : False
            },
            {
                "id": "quit",
                "x": self.button_x_offset, 
                "y": self.button_quit_y_offset,
                "width": 320*4, 
                "height": 224*4, 
                "is_hovered": False,
                "is_pressed" : False
            }
        ]