import arcade
from src.container.main_menu_container import MainMenuContainer
from src.utils import constants


if __name__ == "__main__":
    window = arcade.Window(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, "One Way Ticket" ''', resizable=True''')
    main_menu = MainMenuContainer()
    window.show_view(main_menu)
    arcade.run()