import pygame,time,os,pickle,math
from pygame.locals import *
from settings import *
from sprites import *
from boton import Boton
from map import Map
from camera import Camera

class Game():
    def __init__(self):
        #initialise pygame(window,mixer,clock,etc)
        self.running = True
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display = pygame.Surface(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        self.debug_on = False
        self.ASSETS = {}
        self.load_assets()
        self.LEVELS = self.load_levels()
    
    #Start a new game(SE)
    def new_game(self,level:int):
        self.all_sprites = pygame.sprite.Group()
        self.all_tiles = pygame.sprite.Group()
        self.all_enemies = pygame.sprite.Group()
        self.all_bullets = pygame.sprite.Group()
        self.player_and_tiles = pygame.sprite.Group()
        self.player_group = pygame.sprite.GroupSingle()
        map = Map(self.LEVELS[level])
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT, map, self, DISPLAY_SIZE)
        self.setup_level(map.data,map.pixelWidth)
        

        self.run()
    
    #Game Loop
    def run(self):
        self.playing = True
        self.prev_time = self.get_time()
        while self.playing:
            self.dt = self.get_deltaTime()
            self.prev_time = self.get_time()

            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)
    
    #Game Loop: - Events(SE)
    def events(self):
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
                        self.player.Jkey_pressed = True
                        self.player.jump(self.player.canJump())
                    

                if event.key == pygame.K_BACKSLASH:
                        self.debug_on = not self.debug_on
                        
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                if event.key in [K_SPACE, K_UP]:
                    self.player.Jkey_pressed = False
                
    
    #updates all the game's logic(SE)
    def update(self):
        #Game Loop: - Update
        self.update_sprites()
        self.camera.update(self.player)
        self.update_bg_layers_positions()
        
    #Updates all the sprites logic(SE)
    def update_sprites(self):
        for sprite in self.player_and_tiles:
            sprite.update(self.camera.frame.x, self.camera.frame.right)
        
        for enemy in self.all_enemies:
            enemy.update()
            bullet = enemy.attack()
            if bullet != None:
                self.all_bullets.add(bullet)
        
        for bullet in self.all_bullets:
            bullet.update()
        

    #Renders everything(SE) 
    def draw(self):
        #Game Loop: - Draw
        
        #Things drawn in the display
        self.show_background()
        self.draw_sprites()
        
        
        #Things drawn in the window
        self.window.blit(pygame.transform.scale(self.display, WINDOW_SIZE), (0, 0))
        
        if self.debug_on:
            self.debug()
        
        pygame.display.update()
    
    def draw_sprites(self):
        for sprite in self.all_sprites:
            sprite.draw(self.display)

    # Blit's background layers to the display surface(SE)
    def show_background(self):
        self.display.blit(self.ASSETS["BG_LAYERS"][0],(0,0))#SKY
        self.display.blit(self.ASSETS["BG_LAYERS"][1],(self.layer_data[1][0],0))#SUN & CLOUD

        #The rest
        for i in range(2,self.nb_bg_layers) :
            self.display.blit(self.ASSETS["BG_LAYERS"][i],(self.layer_data[i][0],0))
            self.display.blit(self.ASSETS["BG_LAYERS"][i],(self.layer_data[i][1],0))
    
    # Updates the position of all background layers(SE)
    def update_bg_layers_positions(self):
        self.layer_data[1][0] += self.camera.scroll_amount * self.layer_data[1][2]
        
        for i in range(2,len(self.layer_data)):
            self.layer_data[i][0] += self.camera.scroll_amount * self.layer_data[i][2]
            self.layer_data[i][1] = DISPLAY_SIZE[0] + self.layer_data[i][0]
            
            if self.layer_data[i][0] < -DISPLAY_SIZE[0]:
                self.layer_data[i][0] = self.layer_data[i][1]
                self.layer_data[i][1] = DISPLAY_SIZE[0] + self.layer_data[i][0]

            if self.layer_data[i][0] > 0:
                self.layer_data[i][1] = -DISPLAY_SIZE[0] + self.layer_data[i][0]
                if self.layer_data[i][0] > DISPLAY_SIZE[0]:
                    self.layer_data[i][0] = self.layer_data[i][1]

        

    #Gets current time
    def get_time(self):
        return time.time()
    
    #Gets time since last frame (dt)
    def get_deltaTime(self):
        return self.get_time() - self.prev_time

    #Finds the ceilling of a given number 
    #The term ceiling describes the nearest integer that’s greater than or equal to a given number.
    # ->param n is a floating point number
    # ->return the ceiling of  n 
    def ceiling(self, n:float):
        return math.ceil(n)
    
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
                return 1



            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))
            
            self.window.blit(pygame.transform.scale(self.display, WINDOW_SIZE), (0, 0))
            
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
        self.camera.show_thresholds(self.window)
        self.window.blit(self.update_fps(),(10,10))
        self.window.blit(self.show_playerMoveVector(),(10,30))
        self.window.blit(self.show_DeltaTime(),(10,50))
        self.window.blit(self.show_player_pos(),(10,70))
        #self.window.blit(self.show_player_on_ground(),(10,100))
        #self.window.blit(self.show_player_air_timer(),(10,130))
        #self.window.blit(self.show_player_jumping_b(),(10,160))
        #self.window.blit(self.show_player_jumping_b_timer(),(10,190))
        #self.window.blit(self.show_player_Jkey_pressed(),(10,220))
        #self.window.blit(self.show_player_anim_index(),(10,250))
        self.window.blit(self.show_camera_pos(),(10,280))
        #self.window.blit(self.show_tresholds_pos(),(10,310))
        #self.window.blit(self.show_player_left_and_right_pos(),(10,340))
        self.window.blit(self.show_scroll_amount(),(10,370))
        

    def update_fps(self):
        font = pygame.font.SysFont("Arial",18)
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
        xy = "Display: player: x: " + str(self.player.rect.x) + " y: " + str(self.player.rect.y) + " right: "+ str(self.player.rect.right) 
        xy_text = font.render(xy,1,pygame.Color("coral"))
        return xy_text
    
    def show_DeltaTime(self):
       font = pygame.font.SysFont("Arial", 18) 
       deltaTime = str(round((self.dt) * 1000)) + " ms"
       deltaTime_txt = font.render(deltaTime, 1, pygame.Color("coral"))
       return deltaTime_txt
    
    def show_player_on_ground(self):
       font = pygame.font.SysFont("Arial", 18) 
       on_grnd = "on_ground: " + str(self.player.on_ground)
       on_grnd_txt = font.render(on_grnd, 1, pygame.Color("coral"))
       return on_grnd_txt
    
    def show_player_air_timer(self):
       font = pygame.font.SysFont("Arial", 18) 
       p_air_timer = "air_timer:  " + str(self.player.air_timer)
       p_air_timer_txt = font.render(p_air_timer, 1, pygame.Color("coral"))
       return p_air_timer_txt
    
    def show_player_jumping_b(self):
       font = pygame.font.SysFont("Arial", 18) 
       jumping_b = "jumping:  " + str(self.player.jumping)
       jumping_b_txt = font.render(jumping_b, 1, pygame.Color("coral"))
       return jumping_b_txt
    
    def show_player_jumping_b_timer(self):
       font = pygame.font.SysFont("Arial", 18) 
       jumping_b_timer = "jump_buffer_timer:  " + str(self.player.jump_buffer_timer)
       jumping_b_timer_txt = font.render(jumping_b_timer, 1, pygame.Color("coral"))
       return jumping_b_timer_txt
    
    def show_player_Jkey_pressed(self):
       font = pygame.font.SysFont("Arial", 18) 
       Jkey_pressed = "jKeyPressed:  " + str(self.player.Jkey_pressed)
       Jkey_pressed_txt = font.render(Jkey_pressed, 1, pygame.Color("coral"))
       return Jkey_pressed_txt
    
    def show_player_anim_index(self):
       font = pygame.font.SysFont("Arial", 18) 
       anim_index = "anim_index: " + str(self.player.index)
       anim_index_txt = font.render(anim_index, 1, pygame.Color("coral"))
       return anim_index_txt
    
    def show_camera_pos(self):
       font = pygame.font.SysFont("Arial", 18) 
       camera_pos = "camera : x: " + str(self.camera.frame.x) + " y: " + str(self.camera.frame.y) + " right: " + str(self.camera.frame.right)
       camera_pos_txt = font.render(camera_pos, 1, pygame.Color("coral"))
       return camera_pos_txt
    
    def show_tresholds_pos(self):
       font = pygame.font.SysFont("Arial", 18) 
       tresholds_pos = "A: " + str(self.camera.treshold_A) + " B: " + str(self.camera.treshold_B)
       tresholds_pos_txt = font.render(tresholds_pos, 1, pygame.Color("coral"))
       return tresholds_pos_txt
    
    def show_player_left_and_right_pos(self):
       font = pygame.font.SysFont("Arial", 18) 
       player_left_and_right = "Window pos:player: left: " + str(self.camera.display_px_to_window_px(self.player.rect.left)) + " right: " + str(self.camera.display_px_to_window_px(self.player.rect.right))
       player_left_and_right_txt = font.render(player_left_and_right, 1, pygame.Color("coral"))
       return player_left_and_right_txt
    
    def show_scroll_amount(self):
       font = pygame.font.SysFont("Arial", 18) 
       scroll_amount = "scroll_amount : " + str(self.camera.scroll_amount)
       scroll_amount_txt = font.render(scroll_amount, 1, pygame.Color("coral"))
       return scroll_amount_txt


    #Loading functions

    #loads menu background /game background / botones/ tile image assets(SE)
    def load_assets(self):
        menu_images = []
        temp_bg_layers = []
        bg_layers = []
        botones_images = []
        tiles = []
        self.layer_data = []

        self.nb_bg_layers = len(os.listdir(f"images/background_imgs"))
        nb_menu_frames = len(os.listdir(f"images/menu_imgs"))
        nb_botones = len(os.listdir(f"images/botones"))
        nb_tiles = len(os.listdir(f"images/tiles"))
        
        

        #Loads bg_frames
        for i in range(self.nb_bg_layers):
            temp_bg_layers.append(pygame.image.load(f"images/background_imgs/background_{i}.png").convert_alpha())
        
        #Loads data for the background layers
        sub_v = 1/(self.nb_bg_layers - 2)#value that gets substracted to the speed of the layer(for the parallax effect)
        self.layer_data.append([0,0,0])#sky layer data
        self.layer_data.append([0,0,0.01])# sun & cloud layer data
        max_index = self.nb_bg_layers - 1

        for index in range(1,max_index):
            self.layer_data.append([0,0,0 + (index) * sub_v] )#0: X1(blit position 1) 1: X2 (blit position 2) 2:speed 3:current_treshold
            
        self.layer_data[max_index][2] = 1 - 0.09  

        #Transform frames to the right size
        for frame in temp_bg_layers:
            bg_layers.append(pygame.transform.scale(frame,DISPLAY_SIZE))
            
            


        #loads menu_frames
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
        self.ASSETS["BG_LAYERS"] = bg_layers
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

    def setup_level(self,map_layout,map_width):
        for row,tiles in enumerate(map_layout):
            for col, tile in enumerate(tiles):
                if tile == 0:
                    Tile(self, self.ASSETS["TILES"][0], (col,row))
                if tile == 1:
                    self.player = Player(self,(col, row ), map_width, 
                                         self.camera.window_px_to_display_px(self.camera.treshold_A), 
                                         self.camera.window_px_to_display_px(self.camera.treshold_B))
                if tile == 2:
                    Enemy(self,(col, row))


G = Game()

while G.running:
    G.new_game(G.menu_screen())

pygame.quit()

