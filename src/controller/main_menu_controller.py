import arcade
from ..container.settings_container import SettingsViewContainer
from ..utils.game_settings import GameSettings

class MainMenuController:
    def __init__(self, model, container, game_settings : GameSettings):
        self.model = model
        self.container = container # Reference to the arcade.View to handle transitions
        self.settings = game_settings

    def on_mouse_motion(self, x, y, dx, dy):
        # Check if the mouse is hovering over any button
        for option in self.model.options:
            
            if (option["x"]  < x < option["x"] + option["width"]) and \
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
            print("Transitioning to Game View...")
            # Here you will instantiate your GameView container and switch to it
            # game_view = GameContainer()
            # self.container.window.show_view(game_view)
        elif action_id == "settings":
            print("Going to settings...")
            settings_view = SettingsViewContainer(self.container, self.settings)
            self.container.window.show_view(settings_view)
        else:
            print("Exiting...")
            arcade.exit()