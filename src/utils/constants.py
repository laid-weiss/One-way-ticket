from pathlib import Path

HOME_DIR = Path(__file__).resolve().parent.parent.parent

SCREEN_WIDTH_IN_PIXELS = 320
SCREEN_HEIGHT_IN_PIXELS = 224

# Global pixel-art scale. Every drawing formula in the game scene goes through it.
PIXEL_SIZE = 2

SCREEN_WIDTH = int(SCREEN_WIDTH_IN_PIXELS * PIXEL_SIZE)
SCREEN_HEIGHT = int(SCREEN_HEIGHT_IN_PIXELS * PIXEL_SIZE)
SCREEN_TITLE = "One way Ticket"

MAIN_FONT_PATH = HOME_DIR / "assets" / "general" / "main_font.otf"
MAIN_FONT_NAME = "Lower Pixel"
SETTINGS_FILE = HOME_DIR / "settings.json"

# Developer knobs ---------------------------------------------------------
# Move this point to shift the whole game UI in design pixels. Coordinates are
# measured from the top-left corner of frame.png before PIXEL_SIZE scaling.
GAME_UI_ORIGIN_TOP_LEFT_PIXELS = (0, 0)

# The black placeholder area inside frame.png. map.png is drawn over it.
MAP_TOP_LEFT_PIXELS = (60, 12)
MAP_SIZE_PIXELS = (200, 180)

TRAIN_CARD_SIZE_PIXELS = (32, 50)
ROUTE_CARD_SIZE_PIXELS = TRAIN_CARD_SIZE_PIXELS
TRAIN_CHIP_SIZE_PIXELS = (16, 16)
PLAYER_PLATE_SIZE_PIXELS = (52, 24)
CLOSED_TRAIN_DECK_BUTTON_SIZE_PIXELS = (52, 20)

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0),
    'PINK': (255, 192, 203),
    'GRAY': (128, 128, 128),
}

MAX_PLAYERS = 4
MIN_PLAYERS = 2
TRAIN_CARDS_PER_COLOR = 12
LOCOMOTIVE_CARDS = 14
OPEN_CARDS = 5
INITIAL_TRAIN_CARDS = 4
INITIAL_DESTINATION_TICKETS = 3
INITIAL_DESTINATION_TICKETS_MIN_KEEP = 2
DRAW_DESTINATION_TICKETS = 3
REMAINING_TRAIN_CHIPS_PER_PLAYER = 45

# Backward-compatible name used by old code/tests.
remaining_train_chips_PER_PLAYER = REMAINING_TRAIN_CHIPS_PER_PLAYER
