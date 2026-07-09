import arcade

from ..model.main_menu_model import MainMenuModel
from ..view.main_menu_view import MainMenuView
from ..controller.main_menu_controller import MainMenuController
from ..utils.game_settings import GameSettings


class MainMenuContainer(arcade.View):
    def __init__(self):
        super().__init__()

        self.model = MainMenuModel(self)
        self.view = MainMenuView(self.model, self)
        self.settings = GameSettings.load()
        self.controller = MainMenuController(self.model, self, self.settings)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        self.clear()
        self.view.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.controller.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.controller.on_mouse_press(x, y, button, modifiers)
