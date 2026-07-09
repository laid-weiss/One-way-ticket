import arcade

from ..model.settings_model import SettingsModel
from ..view.settings_view import SettingsGraphicsView
from ..controller.settings_controller import SettingsController
from ..utils.game_settings import GameSettings


class SettingsViewContainer(arcade.View):
    def __init__(self, main_menu_view, settings: GameSettings):
        super().__init__()
        self.main_menu_view = main_menu_view
        self.settings = settings

        self.model = SettingsModel(settings)
        self.graphics_view = SettingsGraphicsView(self.model)
        self.controller = SettingsController(self.model, self.go_back_to_menu, settings)

    def on_draw(self):
        self.clear()
        self.graphics_view.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.controller.on_mouse_press(x, y, button, modifiers)

    def go_back_to_menu(self):
        self.window.show_view(self.main_menu_view)
