import arcade

from ..container.settings_container import SettingsViewContainer
from ..container.game_container import GameContainer
from ..utils.game_settings import GameSettings


class MainMenuController:
    def __init__(self, model, container, game_settings: GameSettings):
        self.model = model
        self.container = container
        self.settings = game_settings

    def on_mouse_motion(self, x, y, dx, dy):
        for option in self.model.options:
            if (option["x"] < x < option["x"] + option["width"]) and \
               (option["y"] < y < option["y"] + option["height"]):
                option["is_hovered"] = False
            else:
                option["is_hovered"] = True

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for option in self.model.options:
                if not option["is_hovered"]:
                    self._handle_action(option["id"])

    def _handle_action(self, action_id):
        if action_id == "start":
            game_view = GameContainer(self.settings, main_menu_view=self.container)
            self.container.window.show_view(game_view)
        elif action_id == "settings":
            settings_view = SettingsViewContainer(self.container, self.settings)
            self.container.window.show_view(settings_view)
        else:
            arcade.exit()
