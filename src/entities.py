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
    import pytweening as tween
    from settings import *
    from tilemap import collide_hit_rect

    # Aliases
    vec = pg.math.Vector2

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

def collide_with_group(sprite, group, dir):
    if sprite.game.noclip:
        return
        
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    for hit in hits:
        if isinstance(hit, Entity):
            if hit.type == 'door':
                if hit.open:
                    return

    if dir =='x':
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir =='y':
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Spritesheet:
    def __init__(self, filename, tileSize=16, gap=1):
        self.spritesheet = pg.image.load(filename).convert()
        self.tileSize = tileSize
        self.gap = gap
        self.tiles = []
        self.parse_images()

    def parse_images(self):
        for y in range(int(self.spritesheet.get_height() / self.tileSize)):
            for x in range(int(self.spritesheet.get_width() / self.tileSize)):
                offset_x = x * self.tileSize
                offset_y = y * self.tileSize

                if x > 0:
                    offset_x += self.gap * x
                if y > 0:
                    offset_y += self.gap * y

                self.tiles.append(self.make_image(offset_x, offset_y))

    def make_image(self, x, y):
        # Grab an image out of a larger spritesheet
        image = pg.Surface((self.tileSize, self.tileSize), pg.SRCALPHA)
        image.blit(self.spritesheet, (0, 0), (x, y, self.tileSize, self.tileSize))
        image = pg.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        return image

    def get_sprite(self, index):
        return self.tiles[index]

class Player(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.groups = game.view.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = self.game.player_img

        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center

        self.pos = vec(pos[0], pos[1])
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.inventory = []

    def get_keys(self):
        self.vel.x, self.vel.y = 0, 0
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def update(self):
        self.get_keys()

        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_group(self, self.game.walls, 'x')
        collide_with_group(self, self.game.entities, 'x')

        self.hit_rect.centery = self.pos.y
        collide_with_group(self, self.game.walls, 'y')
        collide_with_group(self, self.game.entities, 'y')

        self.rect.center = self.hit_rect.center

    def has(self, item):
        if item in self.inventory:
            return True
        return False

    def give(self, inventory):
        for item in inventory:
            self.inventory.append(item)

    def use_closest_object(self):
        for entity in self.game.entities:
            dist = self.pos - entity.pos
            if 0 < dist.length() < PLAYER_INTERACT_RANGE:
                entity.use()

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = WALLS_LAYER
        self.groups = game.view.walls
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.rect = pg.Rect(x, y, w, h)

        self.x = x
        self.y = y

        self.rect.x = x
        self.rect.y = y

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, name):
        self._layer = ITEMS_LAYER
        self.groups = game.view.all_sprites, game.view.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = game.item_images[name]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.name = name

        self.pos = pos
        self.rect.center = pos

        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # Bobbing motion
        # The 0.5 shifting halfway the item because it's moving up and down starting from middle
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED

        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

class Mob(pg.sprite.Sprite):
    def __init__(self, game, pos, name):
        self._layer = MOBS_LAYER
        self.groups = game.view.all_sprites, game.view.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = game.mobs_images[name]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hit_rect = self.rect

        self.name = name

        self.pos = vec(pos[0], pos[1])

class Entity(pg.sprite.Sprite):
    def __init__(self, game, pos, name):
        self._layer = ENTITIES_LAYER
        self.groups = game.view.all_sprites, game.view.entities
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = game.entities_images[name][0]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect

        self.name = name
        self.type = ENTITIES[name]['type']
        self.key = ENTITIES[name]['key']
        if self.type == 'chest':
            self.inventory = ENTITIES[name]['inventory']

        self.open = False
        
        self.pos = pos

        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def use(self):
        if self.key != '':
            if not self.game.player.has(self.key):
                return

        self.image = self.game.entities_images[self.name][1]
        if self.type == 'chest':
            self.game.player.give(self.inventory)
            self.inventory = []
        if self.type == 'door':
            self.open = True

class Trigger(pg.sprite.Sprite):
    def __init__(self, game, pos, w, h, name):
        self._layer = TRIGGERS_LAYER
        self.groups = game.view.triggers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.rect = pg.Rect(pos[0], pos[1], w, h)

        self.name = name
        self.destination = None

        self.action = TRIGGERS[name]['action']
        if self.action == 'teleport':
            self.destination = TRIGGERS[name]['destination']

        self.rect.x = pos[0]
        self.rect.y = pos[1]

class Passage(pg.sprite.Sprite):
    def __init__(self, game, pos, w, h, name):
        self._layer = PASSAGES_LAYER
        self.groups = game.view.passages
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        self.rect = pg.Rect(pos[0], pos[1], w, h)

        self.name = name

        self.pos = pos
        self.rect.x = pos[0]
        self.rect.y = pos[1]

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