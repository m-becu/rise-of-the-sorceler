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

# Maps
MAPS = [
    'level0.tmx',
    'level1.tmx',
    'level2.tmx'
]

# Player settings
PLAYER_SPRITE = 25
PLAYER_SPEED = 300
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 45)
PLAYER_INTERACT_RANGE = 120

# GUI related
HEART_SPRITE = 749

# Mobs
MOBS_SPRITES = {
    'guard': 29
}
MOBS = {}
MOBS['jail_guardian'] = {
    'sprite': MOBS_SPRITES['guard']
}

# Entities
ENTITIES_SPRITES = {
    'chest_clsd': 206,
    'chest_open': 207,
    'jail_clsd': 104,
    'jail_open': 105,
    'breakable_wall_1': 429,
    'broken_wall_1': 571
}
ENTITIES = {}
ENTITIES['jail_chest_0'] = {
    'type': 'chest',
    'key': '',
    'inventory': ['iron_pickaxe'],
    'sprite1': ENTITIES_SPRITES['chest_clsd'],
    'sprite2': ENTITIES_SPRITES['chest_open']
}
ENTITIES['jail_door_0'] = {
    'type': 'door',
    'key': 'guardian_key_0',
    'sprite1': ENTITIES_SPRITES['jail_clsd'],
    'sprite2': ENTITIES_SPRITES['jail_open']
}
ENTITIES['breakable_wall_1'] = {
    'type': 'door',
    'key': 'iron-pickaxe',
    'sprite1': ENTITIES_SPRITES['breakable_wall_1'],
    'sprite2': ENTITIES_SPRITES['broken_wall_1'],
}

# PassagePoints
PASSAGES = {}
PASSAGES['to_jail'] = {
    'location': MAPS[1],
    'x': 0,
    'y': 0
}
PASSAGES['from_jail'] = {
    'location': MAPS[2],
    'x': 0,
    'y': 0
}

# Triggers
TRIGGERS = {}
TRIGGERS['jail_event_0'] = {
    'action': 'event',
    'event': 0
}
TRIGGERS['jail_upstairs'] = {
    'action': 'teleport',
    'destination': 'from_jail'
    }
TRIGGERS['jail_downstairs'] = {
    'action': 'teleport',
    'destination': 'to_jail'
}

# Items
ITEMS = [
    'pickaxe',
    'sword'
]
ITEM_SPRITES = {
    'pickaxe': 902
}

# Layers
WALLS_LAYER = 1
PLAYER_LAYER = 2
MOBS_LAYER = 2
ENTITIES_LAYER = 3
TRIGGERS_LAYER = 4
PASSAGES_LAYER = 4
ITEMS_LAYER = 1

# Fonts
MAIN_FONT = 'unipix.ttf'
SECOND_FONT = 'kenney_pixel.ttf'

# Other stuff
DIALOG_LIFETIME = 2500

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