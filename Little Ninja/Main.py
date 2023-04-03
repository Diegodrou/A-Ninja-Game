import pygame,time
from settings import *
from sprites import *

class Game():
    def __init__(self):
        #initialise pygame(window,mixer,clock,etc)
        self.running = True

        pygame.init()
        pygame.display.set_caption(TITLE)
        self.window = pygame.display.set_mode((window_width, window_height))
        self.display = pygame.Surface(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        self.debug_on = True
    
    def new_game(self,level:int):
        #Start a new game
        self.all_sprites = pygame.sprite.Group()
        #self.player = Player(map.spawn(level))
        self.run()

    def run(self):
        #Game Loop
        self.playing = True
        self.prev_time = self.get_time()
        while self.playing:
            self.dt = self.get_deltaTime()
            self.prev_time = self.get_time()

            self.events()
            self.update()
            self.draw()
            self.clock.tick(fps)

    def events(self):
        #Game Loop: - Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        #Game Loop: - Update
        self.all_sprites.update()
    
    def draw(self):
        #Game Loop: - Draw
        
        #Things drawn in the display
        self.display.fill(DARKGREY)
        self.all_sprites.draw(self.display)
        
        #Things drawn in the window
        self.window.blit(pygame.transform.scale(self.display, window_size), (0, 0))
        
        if self.debug_on:
            self.debug("white")
        
        pygame.display.update()
    
    #Gets current time
    def get_time(self):
        return time.time()
    
    #Gets time since last frame (dt)
    def get_deltaTime(self):
        return self.get_time() - self.prev_time 

    def menu_screen(self):
        game_menu = True
        anim_index = 0

    def pause_screen(self):
        pass

    def death_screen(self):
        pass

    def debug(self,color:str):
        #self.draw_grid(color)
        pass
    
    def draw_grid(self,color:str):
        for x in range(0, window_width, TILE_SIZE):
            pygame.draw.line(self.window , color, (x,0) ,(x,window_height) )
        for y in range(0,window_height, TILE_SIZE):
            pygame.draw.line(self.window, color, (0,y), (window_width,y) )


G = Game()

while G.running:
    G.new_game(G.menu_screen())

pygame.quit()

