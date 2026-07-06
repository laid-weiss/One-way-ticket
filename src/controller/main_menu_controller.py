import arcade

class MainMenuController:
    def __init__(self, model, container):
        self.model = model
        self.container = container # Reference to the arcade.View to handle transitions

    def on_mouse_motion(self, x, y, dx, dy):
        # Check if the mouse is hovering over any button
        for option in self.model.options:
            half_w = option["width"] / 2
            half_h = option["height"] / 2
            
            # Simple bounding box collision detection
            if (option["x"] - half_w < x < option["x"] + half_w) and \
               (option["y"] - half_h < y < option["y"] + half_h):
                option["is_hovered"] = True
            else:
                option["is_hovered"] = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for option in self.model.options:
                if option["is_hovered"]:
                    self._handle_action(option["id"])

    def _handle_action(self, action_id):
        if action_id == "start":
            print("Transitioning to Game View...")
            # Here you will instantiate your GameView container and switch to it
            # game_view = GameContainer()
            # self.container.window.show_view(game_view)
        elif action_id == "quit":
            arcade.exit()