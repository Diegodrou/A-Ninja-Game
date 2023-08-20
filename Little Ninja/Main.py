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
        pygame.mixer.init()
        pygame.display.set_caption(TITLE)
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display = pygame.Surface(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        self.debug_on = False
        self.ASSETS = {}
        self.load_assets()
        self.LEVELS = self.load_levels()
        self.Fps = 60
    
    #Start a new game(SE)
    def new_game(self,level:int):
        self.retry_game = True
        while self.retry_game:
            #All sprite Groups
            self.all_sprites = pygame.sprite.Group()
            self.all_tiles = pygame.sprite.Group()
            self.all_enemies = pygame.sprite.Group()
            self.all_bullets = pygame.sprite.Group()
            self.player_and_tiles = pygame.sprite.Group()
            self.player_group = pygame.sprite.GroupSingle()
            self.attack_sprite = pygame.sprite.GroupSingle()
            #Pause menu stuff
            self.game_pause:bool = False
            self.quit_b_pause:Boton = Boton(270, 180, self.ASSETS["BOTONES_IMGS"][6], 0.5)
            PAUSE_STRING = "PAUSED"
            self.font_pause = pygame.font.SysFont('Arial', 60)
            self.PAUSE_TEXT = self.font_pause.render(PAUSE_STRING, 1, pygame.Color('Red'))
            self.resume_b :Boton = Boton(270, 120, self.ASSETS["BOTONES_IMGS"][7],0.5)
            
            #Dead menu stuff
            self.DEAD_MESAGE_STRING = "U dead"
            self.DEAD_MESAGE_TXT = self.font_pause.render(self.DEAD_MESAGE_STRING, 1, pygame.Color('Red'))
            self.retry_b : Boton = Boton(270, 120, self.ASSETS["BOTONES_IMGS"][8], 0.5)
            self.quit_b_dead_menu:Boton = Boton(270, 180, self.ASSETS["BOTONES_IMGS"][6], 0.5)
            #More game setup stuff
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
            self.clock.tick(self.Fps)
    
    #Game Loop: - Events(SE)
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                    self.retry_game = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_pause:
                        self.game_pause = False
                    else:
                        self.game_pause = True
                if event.key == pygame.K_RIGHT:
                        self.player.moving_right = True
                if event.key == pygame.K_LEFT:
                        self.player.moving_left = True
                if event.key in [K_SPACE, K_UP]:
                        self.player.Jkey_pressed = True
                        self.player.jump(self.player.canJump())
                if event.key == pygame.K_f:
                    if self.player.attack != True:
                        #self.ASSETS["SFX"][4].play()
                        self.player.attack_performed = True
                        self.player.attack = True
                    

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
        if not self.player.dead:
            if not self.game_pause:
                self.enemy_sprite_count_before = self.update_enemy_sprite_count()
                self.update_sprites()
                self.enemy_sprite_count_after = self.update_enemy_sprite_count()
                self.camera.update(self.player)
                self.update_bg_layers_positions()
                self.play_sounds()
                
        
            self.pause_screen_logic()
        self.dead_menu_logic()

    def play_sounds(self):
        if self.player.attack_performed and not self.any_enemy_dead() :
            self.player.attack_performed = False
            self.ASSETS["SFX"][4].play()
        elif self.player.attack_performed and self.any_enemy_dead():
            self.player.attack_performed = False
            self.ASSETS["SFX"][3].play()
    
    def update_enemy_sprite_count(self):
        return self.all_enemies.sprites()
    
    def any_enemy_dead(self):
        if self.enemy_sprite_count_before != self.enemy_sprite_count_after:
            return True     
    #Updates all the sprites logic(SE)
    def update_sprites(self):
        for sprite in self.player_and_tiles:
            sprite.update(self.camera.frame.x, self.camera.frame.right)

        self.attack_sprite.update()
        
        for enemy in self.all_enemies:
            enemy.update()
            enemy.attack()
        
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
        
        self.pause_screen_draw()
        self.dead_menu_draw()

        pygame.display.update()
    
    #Draws all sprites(SE)
    def draw_sprites(self):
        #for sprite in self.all_sprites:
        #    sprite.draw(self.display)
        
        for tile in self.all_tiles:
            tile.draw(self.display)

        for enemy in self.all_enemies:
            enemy.draw(self.display)
        
        for bullet in self.all_bullets:
            bullet.draw(self.display)

        for player in self.player_group:
            player.draw(self.display)


        if self.player.attack and self.debug_on:
            self.attack_sprite.draw(self.display)

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
        play_b:Boton = Boton(10,120,BOTONES_IMGS[0],0.5)


        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            #All Updates
            if play_b.check_click() :
                return self.level_selection_menu()



            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))

            self.display.blit(self.GAME_TITLE_IMG,(5,5))
            
            self.window.blit(pygame.transform.scale(self.display, WINDOW_SIZE), (0, 0))
            
            play_b.draw(self.window)
            
            
            pygame.display.update()
            self.clock.tick(fps)
            
            if (self.get_time() - update_time_m > MAIN_MENU_ANIM_COOLDOWN):
                update_time_m = self.get_time()
                if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                    anim_index = 0
                else:
                    anim_index += 1    
    
    #Menu where the player chooses the level he wants to play(SE)
    # -> returns an interger that represents the level that will be loaded     
    def level_selection_menu(self):
        game_menu:bool = True
        anim_index:int = 0
        BACKGROUND_ANIM:list[pygame.Surface] = self.ASSETS["MENU_FRAMES"]
        BOTONES_IMGS:list[pygame.Surface] = self.ASSETS["BOTONES_IMGS"]
        MAIN_MENU_ANIM_COOLDOWN:float = 0.09
        update_time_m = self.get_time()

        #Intances de botones
        LEVEL_1:Boton = Boton(211,10,BOTONES_IMGS[1], 0.5)
        LEVEL_2:Boton = Boton(307, 10, BOTONES_IMGS[2], 0.5)
        LEVEL_3:Boton = Boton(403,10,BOTONES_IMGS[3], 0.5)
        LEVEL_4:Boton = Boton(500,10,BOTONES_IMGS[4], 0.5)
        LEVEL_5:Boton = Boton(211, 60, BOTONES_IMGS[5], 0.5)

        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            #All Updates
            if LEVEL_1.check_click() :
                return 1
            if LEVEL_2.check_click():
                return 2
            if LEVEL_3.check_click():
                return 3
            if LEVEL_4.check_click():
                return 4
            if LEVEL_5.check_click():
                return 5
            
            
            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))

            self.display.blit(self.GAME_TITLE_IMG,(5,5))
            
            self.window.blit(pygame.transform.scale(self.display, WINDOW_SIZE), (0, 0))
            
            LEVEL_1.draw(self.window)
            LEVEL_2.draw(self.window)
            LEVEL_3.draw(self.window)
            LEVEL_4.draw(self.window)
            LEVEL_5.draw(self.window)
            
            
            pygame.display.update()
            self.clock.tick(fps)
            
            if (self.get_time() - update_time_m > MAIN_MENU_ANIM_COOLDOWN):
                update_time_m = self.get_time()
                if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                    anim_index = 0
                else:
                    anim_index += 1 
    def dead_menu_logic(self):
        if self.player.dead:
            if self.retry_b.check_click():
                self.playing = False
            if self.quit_b_dead_menu.check_click():
                self.playing = False
                self.retry_game = False

    def dead_menu_draw(self):
        if self.player.dead:
            pygame.draw.rect(self.window, (255, 120, 219),
                             pygame.Rect(150, 30, 300, 300), 0, 3)
            self.window.blit(self.DEAD_MESAGE_TXT, (80, 60))
            self.retry_b.draw(self.window)
            self.quit_b_dead_menu.draw(self.window)
    #Draw's the entire pause screen(SE)
    def pause_screen_draw(self):
        if self.game_pause:
            pygame.draw.rect(self.window, (255, 120, 219),
                             pygame.Rect(150, 30, 300, 300), 0, 3)
            
            self.window.blit(self.PAUSE_TEXT,(230,10))
            
            self.quit_b_pause.draw(self.window)
    
    #Updates the logic of all the buttons that appear in the pause menu(SE) 
    def pause_screen_logic(self):
        if self.game_pause:
            if self.quit_b_pause.check_click():
                self.playing = False
                self.retry_game = False

    def death_screen(self):
        pass
    #Debug functions
    def debug(self):
        #self.camera.show_thresholds(self.window)
        self.window.blit(self.update_fps(),(10,10))
        #self.window.blit(self.show_playerMoveVector(),(10,30))
        #self.window.blit(self.show_DeltaTime(),(10,50))
        #self.window.blit(self.show_player_pos(),(10,70))
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
        sounds = []

        self.nb_bg_layers = len(os.listdir(f"images/background_imgs"))
        nb_menu_frames = len(os.listdir(f"images/menu_imgs"))
        nb_botones = len(os.listdir(f"images/botones"))
        nb_tiles = len(os.listdir(f"images/tiles"))
        nb_sounds = len(os.listdir(f"sounds"))
        self.GAME_TITLE_IMG = pygame.image.load(f"images/GameTitleAttempt2.png")

        #Loads bg_frames
        for i in range(self.nb_bg_layers):
            temp_bg_layers.append(pygame.image.load(f"images/background_imgs/background_{i}.png").convert_alpha())
        
        #Loads data for the background layers
        sub_v = 1/(self.nb_bg_layers - 2)#value that gets substracted to the speed of the layer(for the parallax effect)
        self.layer_data.append([0,0,0])#sky layer data
        self.layer_data.append([0,0,0.01])# sun & cloud layer data
        max_index = self.nb_bg_layers - 1

        for index in range(1,max_index):
            self.layer_data.append([0,0,0 + (index) * sub_v] )#0: X1(blit position 1) 1: X2 (blit position 2) 2:speed
            
        self.layer_data[max_index][2] = 1 - 0.09  #closest layer to the player

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

        #Load game sounds
        #0:player_jump 1:player_walking 2:shooting 3:sword_hit_enemy 4:sword slash
        for q in range(nb_sounds):
            sounds.append(pygame.mixer.Sound(os.path.join("sounds",f'{q}.wav')))


        self.ASSETS["BOTONES_IMGS"] = botones_images
        self.ASSETS["MENU_FRAMES"] = menu_images
        self.ASSETS["BG_LAYERS"] = bg_layers
        self.ASSETS["TILES"] = tiles
        self.ASSETS["SFX"] = sounds 
    
    #loods levels using pickle library  
    def load_levels(self):
        lvls = []
        nb_levels = len(os.listdir(f"Levels"))
        for k in range (nb_levels):
                pickle_in = open(f'Levels/level{k}_data', 'rb')
                lvl = pickle.load(pickle_in)
                lvls.append(lvl)
        
        return lvls
    #Setups all the sprites of the level
    def setup_level(self,map_layout:list[list],map_width:int):
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

