# # # # # # # # # # # # # # # # # # # # # # # # # # #
# game.py                                           #
#                                                   #
# Rise of the Sorceler                              #
# A simple 2d rogue-like game                       #
#                                                   #
# Released under the GNU General Public License     #
# Made by An0rak                                    #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

VERSION = "0.1"

try:
    # System
    import sys
    from os import path
    # Game related
    import pygame as pg
    from settings import *
    from tilemap import TiledMap
    from entities import *

    # Aliases
    vec = pg.math.Vector2

except ImportError as err:
    print("Couldn't load module. {err}")
    sys.exit(2)

class Game:
    def __init__(self):
        pg.init()
        self.dimensions = (WIDTH, HEIGHT)
        self.screen = pg.display.set_mode(self.dimensions)
        self.clock = pg.time.Clock()

        pg.display.set_caption(TITLE)
        # pg.key.set_repeat(500, 100)

        self.current_map = MAPS[1]

        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        
        maps_folder = path.join(game_folder, 'maps')
        assets_folder = path.join(game_folder, 'assets')
        
        fonts_folder = path.join(assets_folder, 'fonts')
        
        self.spritesheet = Spritesheet(path.join(assets_folder, SPRITESHEET))

        self.player_img = self.spritesheet.get_sprite(PLAYER_SPRITE)

        self.main_font = path.join(fonts_folder, MAIN_FONT)

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 188))

        self.map = TiledMap(path.join(maps_folder, self.current_map))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.passages_pos = {}

        self.item_images = {}
        for item in ITEM_SPRITES:
            temp_image = self.spritesheet.get_sprite(ITEM_SPRITES[item])
            self.item_images[item] = pg.transform.scale(temp_image, (TILE_SIZE - int(TILE_SIZE/8), TILE_SIZE - int(TILE_SIZE/8)))

        self.mobs_images = {}
        for mob in MOBS:
            self.mobs_images[mob] = self.spritesheet.get_sprite(MOBS[mob]['sprite'])

        self.entities_images = {}
        for entity in ENTITIES:
            sprite1 = self.spritesheet.get_sprite(ENTITIES[entity]['sprite1'])
            sprite2 = self.spritesheet.get_sprite(ENTITIES[entity]['sprite2'])
            self.entities_images[entity] = (sprite1, sprite2)

    def new(self, past=False):
        # Initialization and setup
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.entities = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.triggers = pg.sprite.Group()
        self.passages = pg.sprite.Group()

        for tile_object in self.map.tmxdata.objects:

            tile_object.x *= int(TILE_SIZE / self.map.tilesize)
            tile_object.y *= int(TILE_SIZE / self.map.tilesize)

            obj_center = vec(tile_object.x + tile_object.width / 2 + 12, tile_object.y + tile_object.height / 2 + 12)
            # I still can't figure out why I have to 
            # hard-code an offset of 12 pixels for the positions of the entities.

            if tile_object.name == 'player':
                self.player = Player(self, obj_center)

            elif tile_object.name in ITEMS:
                Item(self, obj_center, tile_object.name)

            elif tile_object.name in MOBS:
                Mob(self, obj_center, tile_object.name)

            else:
                tile_object.width *= int(TILE_SIZE / self.map.tilesize)
                tile_object.height *= int(TILE_SIZE / self.map.tilesize)

            if tile_object.name in ENTITIES:
                pos = (tile_object.x, tile_object.y)
                Entity(self, pos, tile_object.name)

            if tile_object.name in TRIGGERS:
                pos = (tile_object.x, tile_object.y)
                Trigger(self, pos, tile_object.width, tile_object.height, tile_object.name)

            if tile_object.name in PASSAGES:
                pos = (tile_object.x, tile_object.y)
                self.passages_pos[tile_object.name] = pos
                Passage(self, pos, tile_object.width, tile_object.height, tile_object.name)

            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)


        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False
        if not past:
            self.draw_debug = False
            self.noclip = False

    def run(self):
        # Game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

        triggers = pg.sprite.spritecollide(self.player, self.triggers, False, collide_hit_rect)
        for trigger in triggers:
            if trigger.action == 'teleport':
                self.travel_to(trigger.destination)

    def travel_to(self, dest):
        dest_map = PASSAGES[dest]['location']
        self.current_map = dest_map

        self.load_data()
        self.new(past=True)

        dest_pos = self.passages_pos[dest]
        self.player.vel = vec(0, 0)
        self.player.pos = dest_pos

    def draw_grid(self):
        for x in range(0, WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (0, y), (WIDTH, y))

    def draw(self):
        # Draw stuff here
        self.screen.fill(BG_COLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()

        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                self.all_sprites.move_to_front(sprite)

            self.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(wall.rect), 1)
            for trigger in self.triggers:
                pg.draw.rect(self.screen, RED, self.camera.apply_rect(trigger.rect), 1)
            for passage in self.passages:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(passage.rect), 1)

        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("PAUSED", self.main_font, 105, YELLOW, WIDTH / 2, HEIGHT / 2, align='center')

        if self.noclip:
            self.draw_text("NOCLIP", self.main_font, 70, WHITE, WIDTH/10, HEIGHT/10, align='center')
        
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_n:
                    self.noclip = not self.noclip
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_i:
                    print(self.player.inventory)
                if event.key == pg.K_RETURN:
                    self.player.use_closest_object()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.main_font, 180, RED, WIDTH / 2, HEIGHT / 2, align='center')
        self.draw_text("Press a key to start a new game", self.main_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align='center')
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait() # Clears out any event happened before GameOver event
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

g = Game()
g.show_start_screen()

while True:
    g.new()
    g.run()
    g.show_go_screen()