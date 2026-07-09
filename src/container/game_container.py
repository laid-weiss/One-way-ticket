import arcade

from ..controller.game_controller import GameController
from ..model.game_model import GameModel
from ..utils.game_settings import GameSettings
from ..view.game_table_view import GameTableView


class GameContainer(arcade.View):
    """Arcade View container that owns the MVC triad for the main game scene."""

    def __init__(self, settings: GameSettings, main_menu_view=None):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.settings = settings
        self.model = GameModel(settings)
        self.graphics_view = GameTableView(self.model)
        self.controller = GameController(self.model, self, self.graphics_view)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.graphics_view.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.controller.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.controller.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        self.controller.on_key_press(symbol, modifiers)
        
    def go_back_to_menu(self):
        if self.main_menu_view is not None:
            self.window.show_view(self.main_menu_view)
