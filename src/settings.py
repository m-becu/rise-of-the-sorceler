# # # # # # # # # # # # # # # # # # # # # # # # # # #
# settings.py                                       #
#                                                   #
# Rise of the Sorceler                              #
# A simple 2d rogue-like game                       #
#                                                   #
# Released under the GNU General Public License     #
# Made by An0rak                                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

try:
    # System
    import sys
    # Game related
    import pygame as pg

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

# Game settings
WIDTH = 800
HEIGHT = 600

TITLE = "Rise Of The Sorceler"

FPS = 60
TILE_SIZE = 64

SPRITESHEET = 'charset.png'

BOB_RANGE = 15
BOB_SPEED = 0.4

# Player settings
PLAYER_SPRITE = 25
PLAYER_SPEED = 300
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)

# Items
ITEM_SPRITES = {
    'pickaxe': 902
}

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
ITEMS_LAYER = 1

# Fonts
MAIN_FONT = 'kenney_pixel.ttf'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (100, 55, 5)
CYAN = (0, 255, 255)
DEEP_PURPLE = (71, 45, 50)

BG_COLOR = DEEP_PURPLE