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
    from entities import Player, Spritesheet, Camera

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
        pg.key.set_repeat(500, 100)

        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        assets_folder = path.join(game_folder, 'assets')

        self.spritesheet = Spritesheet(path.join(assets_folder, SPRITESHEET))

    def new(self):
        # Initialization and setup for a new game
        self.all_sprites = pg.sprite.Group()

        self.player = Player(self, 5, 5)

        self.camera = Camera(WIDTH, HEIGHT)

    def run(self):
        # Game loop
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw_grid(self):
        for x in range(0, WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (0, y), (WIDTH, y))

    def draw(self):
        # Draw stuff here
        self.screen.fill(BG_COLOR)
        self.draw_grid()

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

g = Game()
g.show_start_screen()

while True:
    g.new()
    g.run()
    g.show_go_screen()