# # # # # # # # # # # # # # # # # # # # # # # # # # #
# entities.py                                       #
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
    from settings import *

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

class Spritesheet:
    def __init__(self):
        pass