import arcade
from src.container.main_menu_container import MainMenuContainer

if __name__ == "__main__":
    window = arcade.Window(1024, 768, "Ticket to Ride Clone")
    main_menu = MainMenuContainer()
    window.show_view(main_menu)
    arcade.run()