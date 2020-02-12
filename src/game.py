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
    from os import listdir
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

class View:
    def __init__(self, game, map, dimensions):
        self.game           = game
        self.map            = TiledMap(path.join(game.maps_folder, map))
        self.map_img        = self.map.make_map()
        self.map_rect       = self.map_img.get_rect()

        self.dimensions     = dimensions
        self.screen         = pg.display.set_mode(self.dimensions)

        self.all_sprites    = game.all_sprites
        self.walls          = game.walls
        self.items          = game.items
        self.entities       = game.entities
        self.mobs           = game.mobs
        self.triggers       = game.triggers
        self.passages       = game.passages

class Game:
    def __init__(self):
        pg.init()
        self.dimensions = (WIDTH, HEIGHT)
        self.screen = pg.display.set_mode(self.dimensions)

        self.clock = pg.time.Clock()

        self.maps = {}
        self.views = {}

        pg.display.set_caption(TITLE)

        self.load_data()

    def load_data(self):
        self.game_folder = path.dirname(__file__)
        
        self.maps_folder = path.join(self.game_folder, 'maps')
        self.assets_folder = path.join(self.game_folder, 'assets')
        self.texts_folder = path.join(self.game_folder, 'txt')
        
        self.fonts_folder = path.join(self.assets_folder, 'fonts')
        
        self.spritesheet = Spritesheet(path.join(self.assets_folder, SPRITESHEET))

        self.player_img = self.spritesheet.get_sprite(PLAYER_SPRITE)
        self.lifebar_img = self.spritesheet.get_sprite(HEART_SPRITE)

        self.main_font = path.join(self.fonts_folder, MAIN_FONT)

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 188))

        maps = [f for f in listdir(path.join(self.maps_folder)) if path.isfile(path.join(path.join(self.maps_folder), f))]
        for map_name in maps:
            if '.tmx' in map_name:
                map = TiledMap(path.join(self.maps_folder, map_name))
                map_img = map.make_map()
                map_rect = map_img.get_rect()
                self.maps[map_name] = (map, map_img, map_rect)

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
        
        self.all_texts = []
        texts = [f for f in listdir(path.join(self.texts_folder)) if path.isfile(path.join(path.join(self.texts_folder), f))]
        for file in texts:
            text = ""
            if '.txt' in file:
                file_text = open(path.join(self.texts_folder, file), 'r')
                for line in file_text.readlines():
                    text += line.strip()
                self.all_texts.append(text)

    def new(self):
        # Initialization and setup
        self.reset_groups()
        self.gui = pg.sprite.Group()

        self.current_map = MAPS[1]
        self.view = View(self, self.current_map, self.dimensions)
        self.views[self.current_map] = self.view

        self.player_spawned = False
        self.zone = None

        self.load_map()

        self.show_dialog = False
        self.show_gui = True
        
        self.draw_debug = False
        self.noclip = False

    def reset_groups(self):
        self.all_sprites    = pg.sprite.LayeredUpdates()
        self.gui            = pg.sprite.Group()
        self.walls          = pg.sprite.Group()
        self.items          = pg.sprite.Group()
        self.entities       = pg.sprite.Group()
        self.mobs           = pg.sprite.Group()
        self.triggers       = pg.sprite.Group()
        self.passages       = pg.sprite.Group()

    def load_groups(self):
        self.all_sprites    = self.view.all_sprites
        self.walls          = self.view.walls
        self.items          = self.view.items
        self.entities       = self.view.entities
        self.mobs           = self.view.mobs
        self.triggers       = self.view.triggers
        self.passages       = self.view.passages

    def load_map(self):
        for tile_object in self.view.map.tmxdata.objects:

                tile_object.x *= int(TILE_SIZE / self.view.map.tilesize)
                tile_object.y *= int(TILE_SIZE / self.view.map.tilesize)

                obj_center = vec(tile_object.x + tile_object.width / 2 + 12, tile_object.y + tile_object.height / 2 + 12)
                # I still can't figure out why I have to 
                # hard-code an offset of 12 pixels for the positions of the entities.

                if tile_object.name == 'player_start' and not self.player_spawned:
                    self.player = Player(self, obj_center)
                    self.player_spawned = True

                elif tile_object.name in ITEMS:
                    Item(self, obj_center, tile_object.name)

                elif tile_object.name in MOBS:
                    Mob(self, obj_center, tile_object.name)

                else:
                    tile_object.width *= int(TILE_SIZE / self.view.map.tilesize)
                    tile_object.height *= int(TILE_SIZE / self.view.map.tilesize)

                if tile_object.name in ENTITIES:
                    pos = (tile_object.x, tile_object.y)
                    Entity(self, pos, tile_object.name)

                if tile_object.name in TRIGGERS:
                    pos = (tile_object.x, tile_object.y)
                    Trigger(self, pos, tile_object.width, tile_object.height, tile_object.name)

                if tile_object.name in PASSAGES:
                    pos = (tile_object.x, tile_object.y)
                    PASSAGES[tile_object.name]['x'] = tile_object.x
                    PASSAGES[tile_object.name]['y'] = tile_object.y
                    Passage(self, pos, tile_object.width, tile_object.height, tile_object.name)

                if tile_object.name == 'wall':
                    Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)

        self.lifebar = Lifebar(self, 10, 10)
        self.camera = Camera(self.view.map.width, self.view.map.height)
        self.paused = False

    def call_event(self, event):
        if event == 0:
            DialogBox(self, self.all_texts[0], (0, HEIGHT * 3/4))

        else:
            print("No event found.")

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
        self.view.all_sprites.update()
        self.gui.update()
        self.camera.update(self.player)

        triggers = pg.sprite.spritecollide(self.player, self.triggers, False, collide_hit_rect)
        for trigger in triggers:
            if trigger.action == 'teleport':
                self.travel_to(trigger.destination)
            if trigger.action == 'event':
                if not trigger.called:
                    self.call_event(trigger.event)
                    trigger.called = True

    def travel_to(self, dest):
        dest_map = PASSAGES[dest]['location']
        self.views[self.current_map] = self.view

        if dest_map not in self.views:
            self.reset_groups()
            self.view = View(self, dest_map, self.dimensions)
            self.view.all_sprites.add(self.player)
            self.load_map()

        else:
            self.view = self.views[dest_map]

        self.load_groups()

        self.current_map = dest_map
        dest_pos = vec(PASSAGES[dest]['x'], PASSAGES[dest]['y'])

        self.player.vel = vec(0, 0)
        self.player.pos = dest_pos

    def draw_text(self, text, font_name, size, color, x, y, align="nw", dest=None):
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
        
        if not dest:
            self.view.screen.blit(text_surface, text_rect)
        else:
            dest.blit(text_surface, text_rect)

    def draw_grid(self):
        for x in range(0, WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (0, y), (WIDTH, y))

    def draw(self):
        # Draw stuff here
        self.view.screen.fill(BG_COLOR)
        self.view.screen.blit(self.view.map_img, self.camera.apply_rect(self.view.map_rect))
        # self.draw_grid()

        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                self.view.all_sprites.move_to_front(sprite)

            self.view.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.draw_debug:
                pg.draw.rect(self.view.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        
        for ui in self.gui:
            if isinstance(ui, Lifebar):
                self.screen.blit(ui.image, (10, 10))
            if isinstance(ui, DialogBox):
                self.screen.blit(ui.image, (0, HEIGHT * 3/4))

        if self.draw_debug:
            pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
            
            for wall in self.walls:
                pg.draw.rect(self.view.screen, YELLOW, self.camera.apply_rect(wall.rect), 1)
            for trigger in self.triggers:
                pg.draw.rect(self.view.screen, RED, self.camera.apply_rect(trigger.rect), 1)
            for passage in self.passages:
                pg.draw.rect(self.view.screen, GREEN, self.camera.apply_rect(passage.rect), 1)

        else:
            pg.display.set_caption(TITLE)

        if self.paused:
            self.view.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("PAUSED", self.main_font, 105, YELLOW, WIDTH / 2, HEIGHT / 2, align='center')

        if self.noclip:
            self.draw_text("NOCLIP", self.main_font, 70, WHITE, WIDTH/10, HEIGHT/10, align='center')

        self.screen = self.view.screen
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
                if event.key == pg.K_v:
                    self.player.hurt()
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