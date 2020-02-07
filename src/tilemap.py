# # # # # # # # # # # # # # # # # # # # # # # # # # #
# tilemap.py                                       #
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
    import pytmx
    import pygame as pg
    from settings import *

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * TILE_SIZE
        self.height = tm.height * TILE_SIZE
        self.tilesize = tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        tile = pg.transform.scale(tile,(TILE_SIZE,TILE_SIZE))
                        surface.blit(tile, (x * TILE_SIZE,
                                            y * TILE_SIZE))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA).convert_alpha()
        self.render(temp_surface)
        return temp_surface