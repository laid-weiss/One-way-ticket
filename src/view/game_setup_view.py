import arcade

class MainMenuView:
    def __init__(self, model):
        self.model = model

    def draw(self):
        # Draw the game title
        arcade.draw_text(
            "Ticket to Ride", 
            self.model.options[0]["x"], 
            self.model.options[0]["y"] + 120, 
            arcade.color.WHITE, 
            font_size=48, 
            anchor_x="center", 
            anchor_y="center",
            bold=True
        )

        # Draw the buttons based on model state
        for option in self.model.options:
            # Change color if the controller has marked it as hovered
            bg_color = arcade.color.DARK_PASTEL_BLUE if option["is_hovered"] else arcade.color.BATTLESHIP_GREY
            

            arcade.draw_rect_filled(arcade.Rect.from_kwargs(x=option["x"], y=option["y"], width=option["width"], height=option["height"]), bg_color)
            arcade.draw_text(
                option["text"], 
                option["x"], option["y"], 
                arcade.color.WHITE, 
                font_size=20, 
                anchor_x="center", 
                anchor_y="center"
            )