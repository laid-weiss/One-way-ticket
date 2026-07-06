class MainMenuModel:
    def __init__(self, screen_width, screen_height):
        center_x = screen_width / 2
        
        # Define the buttons/options for the menu
        self.options = [
            {
                "id": "start",
                "text": "Start Game", 
                "x": center_x, 
                "y": screen_height / 2 + 30, 
                "width": 250, 
                "height": 50, 
                "is_hovered": False
            },
            {
                "id": "quit",
                "text": "Quit", 
                "x": center_x, 
                "y": screen_height / 2 - 40, 
                "width": 250, 
                "height": 50, 
                "is_hovered": False
            }
        ]