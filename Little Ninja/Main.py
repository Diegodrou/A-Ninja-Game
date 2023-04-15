import pygame,time,os,pickle
from pygame.locals import *
from settings import *
from sprites import *
from boton import Boton
from map import Map

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
        self.ASSETS = {}
        self.load_assets()
        self.LEVELS = self.load_levels()

    def new_game(self,level:int):
        #Start a new game
        self.all_sprites = pygame.sprite.Group()
        self.all_tiles = pygame.sprite.Group()
        map = Map(self.LEVELS[level])
        self.setup_level(map.data)
        

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
            self.clock.tick(60)

    def events(self):
        #Game Loop: - Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:    
                if event.key == pygame.K_RIGHT:
                        self.player.moving_right = True
                if event.key == pygame.K_LEFT:
                        self.player.moving_left = True
                if event.key in [K_SPACE, K_UP]:
                    if self.player.air_timer < 7:
                        self.player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                
    
    #updates all the game's logic
    def update(self):
        #Game Loop: - Update
        for sprite in self.all_sprites:
            sprite.update()
    
    #Renders everything 
    def draw(self):
        #Game Loop: - Draw
        
        #Things drawn in the display
        self.display.fill(DARKGREY)
        for sprite in self.all_sprites:
            sprite.draw(self.display)
        
        #Things drawn in the window
        self.window.blit(pygame.transform.scale(self.display, window_size), (0, 0))
        
        if self.debug_on:
            self.debug()
        
        pygame.display.update()
    
    #Gets current time
    def get_time(self):
        return time.time()
    
    #Gets time since last frame (dt)
    def get_deltaTime(self):
        return self.get_time() - self.prev_time 
    
    #Menu Loop
    def menu_screen(self):
        game_menu:bool = True
        anim_index:int = 0
        BACKGROUND_ANIM:list[pygame.Surface] = self.ASSETS["MENU_FRAMES"]
        BOTONES_IMGS:list[pygame.Surface] = self.ASSETS["BOTONES_IMGS"]
        MAIN_MENU_ANIM_COOLDOWN:float =0.09
        update_time_m = self.get_time()

        #Intances de botones
        level_1_b:Boton = Boton(10,10,BOTONES_IMGS[0],0.5)


        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            #All Updates
            if level_1_b.check_click() :
                return 0



            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))
            
            self.window.blit(pygame.transform.scale(self.display, window_size), (0, 0))
            
            level_1_b.draw(self.window)
            
            
            pygame.display.update()
            self.clock.tick(fps)
            
            if (self.get_time() - update_time_m > MAIN_MENU_ANIM_COOLDOWN):
                update_time_m = self.get_time()
                if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                    anim_index = 0
                else:
                    anim_index += 1    
            


    def pause_screen(self):
        pass

    def death_screen(self):
        pass
    #Debug functions
    def debug(self):
        self.window.blit(self.update_fps(),(10,10))
        self.window.blit(self.show_playerMoveVector(),(10,30))
        self.window.blit(self.show_DeltaTime(),(10,50))
        self.window.blit(self.show_player_pos(),(10,70))
        self.window.blit(self.show_Y_current(),(10,100))

    def update_fps(self):
        font = pygame.font.SysFont("Arial", 18)
        fps = str(int(self.clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("coral"))
        return fps_text
    
    def show_playerMoveVector(self):
       font = pygame.font.SysFont("Arial", 18) 
       move_vector = "velocity : "+ str(self.player.velocity)
       move_vector_txt = font.render(move_vector, 1, pygame.Color("coral"))
       return move_vector_txt
    
    def show_player_pos(self):
        font = pygame.font.SysFont("Arial", 18)
        xy = "x: " + str(self.player.rect.x) + " y: " + str(self.player.rect.y) 
        xy_text = font.render(xy,1,pygame.Color("coral"))
        return xy_text

    
    def show_DeltaTime(self):
       font = pygame.font.SysFont("Arial", 18) 
       deltaTime = str((self.dt) * 1000) + " ms"
       deltaTime_txt = font.render(deltaTime, 1, pygame.Color("coral"))
       return deltaTime_txt
    

    def show_Y_current(self):
       font = pygame.font.SysFont("Arial", 18) 
       Y_c = "Y_c: " + str(self.player.y_current_value)
       Y_c_txt = font.render(Y_c, 1, pygame.Color("coral"))
       return Y_c_txt
    #Loading functions

    #loads menu background /game background / botones/ tile image assets
    def load_assets(self):
        menu_images = []
        bg_frames = []
        botones_images = []
        tiles = []

        nb_bg_frames = len(os.listdir(f"images/background_imgs"))
        nb_menu_frames = len(os.listdir(f"images/menu_imgs"))
        nb_botones = len(os.listdir(f"images/botones"))
        nb_tiles = len(os.listdir(f"images/tiles"))
        

        #loads menu_frames
        for i in range(nb_bg_frames):
            bg_frames.append(pygame.image.load(f"images/background_imgs/background_{i}.png").convert())
        
        #loads bg_frames
        for n in range(nb_menu_frames):
            menu_images.append(pygame.image.load(f"images/menu_imgs/{n}.png").convert())
        
        #load imagenes de botones
        for j in range(nb_botones):
            botones_images.append(pygame.image.load(f"images/botones/{j}.png"))
        
        #Load tile images
        for h in range(nb_tiles):
            tiles.append(pygame.image.load(f"images/tiles/{h}.png").convert())


        self.ASSETS["BOTONES_IMGS"] = botones_images
        self.ASSETS["MENU_FRAMES"] = menu_images
        self.ASSETS["BG_FRAMES"] = bg_frames
        self.ASSETS["TILES"] = tiles
    
    #loods levels using pickle library  
    def load_levels(self):
        lvls = []
        nb_levels = len(os.listdir(f"Levels"))
        for k in range (nb_levels):
                pickle_in = open(f'Levels/level{k}_data', 'rb')
                lvl = pickle.load(pickle_in)
                lvls.append(lvl)
        
        return lvls

    def setup_level(self,map_layout):
        for row,tiles in enumerate(map_layout):
            for col, tile in enumerate(tiles):
                if tile == 0:
                    Tile(self, self.ASSETS["TILES"][0], (col,row))
                if tile == 1:
                    self.player = Player(self,(col, row ))
                if tile == 2:
                    pass


G = Game()

while G.running:
    G.new_game(G.menu_screen())

pygame.quit()

