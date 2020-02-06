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

    vec = pg.math.Vector2

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

class Spritesheet:
    def __init__(self, filename, tileSize=16, gap=1):
        self.spritesheet = pg.image.load(filename).convert()
        self.tileSize = tileSize
        self.gap = gap
        self.tiles = []
        self.parse_images()

    def parse_images(self):
        for x in range(int(self.spritesheet.get_width() / self.tileSize)):
            for y in range(int(self.spritesheet.get_height() / self.tileSize)):
                offset_x = x * self.tileSize
                offset_y = y * self.tileSize

                if x > 0:
                    offset_x += self.gap * x
                if y > 0:
                    offset_y += self.gap * y

                print(offset_x, offset_y)

                self.tiles.append(self.make_image(offset_x, offset_y))

    def make_image(self, x, y):
        # Grab an image out of a larger spritesheet
        image = pg.Surface((self.tileSize, self.tileSize))
        image.blit(self.spritesheet, (0, 0), (x, y, self.tileSize, self.tileSize))
        image = pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image

    def get_sprite(self, index):
        return self.tiles[index]

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = self.game.spritesheet.get_sprite(PLAYER_SPRITE).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        pass

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit scrolling
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pg.Rect(x, y, self.width, self.height)