import arcade
from ..model.main_menu_model import MainMenuModel
from ..view.main_menu_view import MainMenuView
from ..controller.main_menu_controller import MainMenuController

class MainMenuContainer(arcade.View):
    def __init__(self):
        super().__init__()
        
        # Instantiate the MVC triad
        # We pass the window dimensions to the model so it can center elements
        self.model = MainMenuModel(self)
        self.view = MainMenuView(self.model, self)
        self.controller = MainMenuController(self.model, self)

    def on_show_view(self):
        # Setup specific to when this view appears
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        self.clear() # Clears the screen
        self.view.draw() # Delegate drawing to the View

    def on_mouse_motion(self, x, y, dx, dy):
        # Delegate input to the Controller
        self.controller.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        # Delegate input to the Controller
        self.controller.on_mouse_press(x, y, button, modifiers)