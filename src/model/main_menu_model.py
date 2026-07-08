from ..utils import constants

#button: 320 x 224
#

class MainMenuModel:
    
    button_x_pixel_offset = 32
    button_start_y_pixel_offset = 99
    button_settings_y_pixel_offset = 78
    button_quit_y_pixel_offset = 57

    button_x_offset = button_x_pixel_offset * constants.PIXEL_SIZE
    button_start_y_offset = button_start_y_pixel_offset * constants.PIXEL_SIZE
    button_settings_y_offset = button_settings_y_pixel_offset * constants.PIXEL_SIZE
    button_quit_y_offset = button_quit_y_pixel_offset * constants.PIXEL_SIZE 
    
    def __init__(self, container):
        
        self.container = container
        
        # Define the buttons/options for the menu
        self.options = [
            {
                "id": "start",
                "x": self.button_x_offset ,
                "y": self.button_start_y_offset,
                "width": constants.PIXEL_SIZE * 92, 
                "height": constants.PIXEL_SIZE * 25, 
                "is_hovered": False,
                "is_pressed" : False
            },
            {
                "id": "settings",
                "x": self.button_x_offset, 
                "y": self.button_settings_y_offset,
                "width": constants.PIXEL_SIZE * 92, 
                "height": constants.PIXEL_SIZE * 20, 
                "is_hovered": False,
                "is_pressed" : False
            },
            {
                "id": "quit",
                "x": self.button_x_offset, 
                "y": self.button_quit_y_offset,
                "width": constants.PIXEL_SIZE * 92, 
                "height": constants.PIXEL_SIZE * 20, 
                "is_hovered": False,
                "is_pressed" : False
            }
        ]