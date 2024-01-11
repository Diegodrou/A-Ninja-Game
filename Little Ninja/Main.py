import pygame,time,os,pickle,math
from pygame.locals import *
from settings import *
from sprites import *
from boton import *
from map import Map
from camera import Camera
import sys

class Game():
    def __init__(self):
        #initialise pygame(window,mixer,clock,etc)
        self.running = True
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)
        pygame.display.set_caption(TITLE)
        self.MONITOR_RESOLUTION = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.get_resolutions()
        self.selected_resolution = 1
        self.res_scale = 1
        self.prev_res_scale = self.res_scale
        self.aqui = False
        self.window = pygame.display.set_mode((self.RESOLUTIONS[self.selected_resolution][0], 
                                               self.RESOLUTIONS[self.selected_resolution][1]),pygame.RESIZABLE)
        self.display = pygame.Surface(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        self.debug_on = False
        self.buttons = []
        self.texts_1 = []
        self.texts_2 = []
        self.strings_1 = []
        self.strings_2 = []
        self.selected_fps = 1
        self.POSSIBLE_FPS = [30,60]
        self.Fps = self.POSSIBLE_FPS[self.selected_fps]
        self.ASSETS = {}
        self.load_assets()
        self.setup_buttons_and_txt()
        self.LEVELS = self.load_levels()
        self.ui_txt_size = 22
        self.ui_font = pygame.font.SysFont('Arial',int(self.ui_txt_size * self.res_scale))
        pygame.mixer.music.load(self.ASSETS["MUSIC_PATHS"][0])
        pygame.mixer.music.play(loops=-1)
        self.win = False

    
    #Start a new game(SE)
    def new_game(self,level:int):
        self.retry_game = True
        self.win = False
        self.current_lvl = level
        if self.music_check_box.state == True:
            pygame.mixer.music.load(self.ASSETS["MUSIC_PATHS"][level])
            pygame.mixer.music.play(loops=-1)
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
            

            
            #More game setup stuff
            
            map = Map(self.LEVELS[level])
            self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT, map, self, DISPLAY_SIZE)
            self.setup_level(map.data,map.pixelWidth)
            self.nb_of_enemies_max:int = self.countEnemies()
            self.nb_enemies_killed:int = 0

            
            if level != -1:
                self.run()
            else:
                self.running = False
                sys.exit(0)
    
    #Game Loop
    def run(self):
        self.update_sound_time = pygame.time.get_ticks()
        self.playing = True
        self.prev_time = self.get_time()
        while self.playing:
            self.dt = self.get_deltaTime()
            self.prev_time = self.get_time()

            self.events()
            self.update()
            self.draw()
            self.clock.tick(self.Fps)
    
    def countEnemies(self):
        return self.all_enemies.__len__()

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
                if not self.win:
                    self.enemy_sprite_count_before = self.update_enemy_sprite_count()
                    self.update_sprites()
                    self.enemy_sprite_count_after = self.update_enemy_sprite_count()
                    self.camera.update(self.player)
                    self.update_bg_layers_positions()
                    self.play_sounds()
                    self.check_win()
                self.win_menu_logic()
            self.pause_screen_logic()
        self.dead_menu_logic()

    def play_sounds(self):
        self.play_attack_sound()
        self.play_jump_sound()
        self.play_player_walking_sound()
        self.play_player_dead_sound()
        self.play_deflect_bullet_sound()
        

    def play_attack_sound(self):
        if not (self.player.moving_left or self.player.moving_right):
            if self.player.attack_performed and not self.any_enemy_dead() :
                self.player.attack_performed = False
                self.ASSETS["SFX"][4].play()
            elif self.player.attack_performed and self.any_enemy_dead():
                self.player.attack_performed = False
                self.ASSETS["SFX"][3].play()

    def play_jump_sound(self):
        if self.player.jump_performed:
            self.player.jump_performed = False
            if not self.player.dead:
                    self.ASSETS["SFX"][0].play()

    def play_player_walking_sound(self):
        if (pygame.time.get_ticks() - self.update_sound_time > self.player.STEPS_SOUND_COOLDOWN) and (self.player.moving_left or self.player.moving_right):
            if self.player.on_ground:
                self.update_sound_time = pygame.time.get_ticks()
                self.ASSETS["SFX"][1].play()

    def play_click_sound(self):
        self.ASSETS["SFX"][6].play()

    def play_player_dead_sound(self):
        if self.player.dead:
            self.ASSETS["SFX"][5].play()

    def play_enemy_walking_sound(self):
        pass
    
    def play_deflect_bullet_sound(self):
        if self.player.bullet_deflected:
            self.player.bullet_deflected = False
            self.ASSETS["SFX"][7].play()

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
        self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
        
        #UI
        self.window.blit(self.draw_enemy_killed_counter(),(10,1))
        
        if self.debug_on:
            self.debug()
        
        
        #menus
        self.draw_win_menu()
        self.pause_screen_draw()
        self.dead_menu_draw()

        pygame.display.update()
        if self.aqui:
            time.sleep(2)
            self.aqui = False
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

    def draw_enemy_killed_counter(self):
        txt:str= "Enemies left: " + str(self.nb_of_enemies_max - self.nb_enemies_killed)
        txt_surface = self.ui_font.render(txt,1, pygame.Color('Red'))
        return txt_surface

    def check_win(self):
        if (self.nb_of_enemies_max - self.nb_enemies_killed) == 0:
            self.win = True

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
    
    
    def setup_buttons_and_txt(self):
            self.font_1 = pygame.font.SysFont('Arial', 60)
            self.font_2 = pygame.font.SysFont('Arial', 30 * self.res_scale)
            self.PAUSE_STRING = "PAUSED"
            self.pause_text = self.font_1.render(self.PAUSE_STRING, 1, pygame.Color('Red'))
            self.DEAD_MESAGE_STRING = "U dead"
            self.dead_mesage_txt = self.font_1.render(self.DEAD_MESAGE_STRING, 1, pygame.Color('Red'))
            self.MUSIC_STRING = "Music"
            self.fps_string = "FPS : " + str(self.Fps)
            self.FULLSCREEN_STRING = "Fullscreen"
            self.WIN_STRING = "U WIN!!!"
            self.win_message_txt = self.font_1.render(self.WIN_STRING,1,pygame.Color('Red'))
            self.music_volume_string = "Music Volume : " + str(pygame.mixer.music.get_volume())
            self.music_txt = self.font_2.render(self.MUSIC_STRING,1,pygame.Color('Red'))
            self.fps_txt = self.font_2.render(self.fps_string,1,pygame.Color('Red'))
            self.fullscreen_txt = self.font_2.render(self.FULLSCREEN_STRING,1,pygame.Color('Red'))
            self.music_volume_txt = self.font_2.render(self.music_volume_string, 1 ,pygame.Color('Red'))
            self.resolution_string =  str(self.window.get_size()[0])+" x "+str(self.window.get_size()[1])
            self.resolution_txt = self.font_2.render(self.resolution_string,1,pygame.Color('Red'))

            #Buttons
            self.retry_b : Boton = Boton(270, 120, self.ASSETS["BOTONES_IMGS"][8], 0.5)
            self.quit_b_dead_menu:Boton = Boton(270, 180, self.ASSETS["BOTONES_IMGS"][6], 0.5)
            self.retry_b_pause: Boton = Boton(270, 120, self.ASSETS["BOTONES_IMGS"][8], 0.5 )
            self.resume_b :Boton = Boton(270, 120, self.ASSETS["BOTONES_IMGS"][7],0.5)
            self.quit_b_pause:Boton = Boton(270, 180, self.ASSETS["BOTONES_IMGS"][6], 0.5)
            self.play_b:Boton = Boton(10,120,self.ASSETS["BOTONES_IMGS"][0],0.5)
            self.option_b = Boton(10, 180, self.ASSETS["BOTONES_IMGS"][10], 0.5)
            self.music_check_box =  CheckBox(100,120, self.ASSETS["BOTONES_IMGS"][11], self.ASSETS["BOTONES_IMGS"][12],True, 0.5)
            self.back_button = Boton(10, 250, self.ASSETS["BOTONES_IMGS"][9], 0.5)
            self.left_arrow = Boton(150, 130,self.ASSETS["BOTONES_IMGS"][14],0.25)
            self.right_arrow = Boton(320, 130, pygame.transform.flip(self.ASSETS["BOTONES_IMGS"][14],True,False), 0.25)
            self.LEVEL_1:Boton = Boton(211,10,self.ASSETS["BOTONES_IMGS"][1], 0.5)
            self.LEVEL_2:Boton = Boton(307, 10, self.ASSETS["BOTONES_IMGS"][2], 0.5)
            self.LEVEL_3:Boton = Boton(403,10,self.ASSETS["BOTONES_IMGS"][3], 0.5)
            self.LEVEL_4:Boton = Boton(500,10,self.ASSETS["BOTONES_IMGS"][4], 0.5)
            self.LEVEL_5:Boton = Boton(211, 60, self.ASSETS["BOTONES_IMGS"][5], 0.5)
            self.fps_arrow = Boton(190,165,pygame.transform.flip(self.ASSETS["BOTONES_IMGS"][14],True,False), 0.25)
            self.fullscreen_checkbox = CheckBox(10,210,self.ASSETS["BOTONES_IMGS"][11], self.ASSETS["BOTONES_IMGS"][12],False, 0.5)
            self.left_music_volume_arrow = Boton(300,240,self.ASSETS["BOTONES_IMGS"][14],0.25)
            self.right_music_volume_arrow = Boton(390, 240,pygame.transform.flip(self.ASSETS["BOTONES_IMGS"][14],True,False), 0.25)
            self.quit_main_menu = Boton(10,220,self.ASSETS["BOTONES_IMGS"][6],0.5)
            self.quit_win_menu = Boton(270, 180, self.ASSETS["BOTONES_IMGS"][6], 0.5)
            self.next_level_arrow = Boton(270,120,self.ASSETS["BOTONES_IMGS"][13],0.5)


            self.buttons.append(self.resume_b)
            self.buttons.append(self.quit_b_pause)
            self.buttons.append(self.retry_b)
            self.buttons.append(self.quit_b_dead_menu)
            self.buttons.append(self.retry_b_pause)
            self.buttons.append(self.play_b)
            self.buttons.append(self.option_b)
            self.buttons.append(self.music_check_box)
            self.buttons.append(self.back_button)
            self.buttons.append(self.left_arrow)
            self.buttons.append(self.right_arrow)
            self.buttons.append(self.LEVEL_1)
            self.buttons.append(self.LEVEL_2)
            self.buttons.append(self.LEVEL_3)
            self.buttons.append(self.LEVEL_4)
            self.buttons.append(self.LEVEL_5)
            self.buttons.append(self.fps_arrow)
            self.buttons.append(self.fullscreen_checkbox)
            self.buttons.append(self.left_music_volume_arrow)
            self.buttons.append(self.right_music_volume_arrow)

    #Menu Loop
    def menu_screen(self):
        
        game_menu:bool = True
        anim_index:int = 0
        BACKGROUND_ANIM:list[pygame.Surface] = self.ASSETS["MENU_FRAMES"]
        MAIN_MENU_ANIM_COOLDOWN:float =0.09
        update_time_m = self.get_time()
        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
               

            #All Updates
            if self.play_b.check_click() :
                self.play_click_sound()
                return self.level_selection_menu()

            if self.option_b.check_click():
                self.play_click_sound()
                self.options_menu()

            if self.quit_main_menu.check_click():
                self.play_click_sound()
                return -1
                

            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))

            self.display.blit(self.GAME_TITLE_IMG,(5,5))
            
            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))
            
            self.play_b.draw(self.window,10 * self.res_scale ,120 * self.res_scale, 0.5 * self.res_scale)
            self.option_b.draw(self.window,10 * self.res_scale, self.res_scale * 180,self.res_scale * 0.5)
            self.quit_main_menu.draw(self.window, 10 * self.res_scale, 240 * self.res_scale, 0.5 * self.res_scale)
            
            
            pygame.display.update()
            self.clock.tick(self.Fps)
            
            if (self.get_time() - update_time_m > MAIN_MENU_ANIM_COOLDOWN):
                update_time_m = self.get_time()
                if anim_index >= len(BACKGROUND_ANIM)-1:  # 24 frames in the animation
                    anim_index = 0
                else:
                    anim_index += 1    
    
    def change_scale(self):
        for resolution in range(len(self.RESOLUTIONS)):
            if self.selected_resolution == resolution:
                self.res_scale = self.resolution_scales[resolution]
        self.ui_font = pygame.font.SysFont('Arial',int(self.ui_txt_size * self.res_scale))
    
    def update_text(self):
        self.font_1 = pygame.font.SysFont('Arial',int(60 * self.res_scale))
        self.dead_mesage_txt = self.font_1.render(self.DEAD_MESAGE_STRING, 1, pygame.Color('Red'))
        self.pause_text = self.font_1.render(self.PAUSE_STRING, 1, pygame.Color('Red'))
        self.win_message_txt = self.font_1.render(self.WIN_STRING, 1, pygame.Color('Red'))

        
        self.font_2 = self.font_2 = pygame.font.SysFont('Arial', int(30 * self.res_scale))
        self.music_txt = self.font_2.render(self.MUSIC_STRING,1,pygame.Color('Red'))
        self.fullscreen_txt = self.font_2.render(self.FULLSCREEN_STRING,1,pygame.Color('Red'))
        
        self.fps_string = "FPS : " + str(self.Fps)
        self.fps_txt = self.font_2.render(self.fps_string,1,pygame.Color('Red'))
        self.resolution_string =  str(self.window.get_size()[0])+" x "+str(self.window.get_size()[1])
        self.resolution_txt = self.font_2.render(self.resolution_string,1,pygame.Color('Red'))
        self.music_volume_string = "Music Volume : " + str(round(pygame.mixer.music.get_volume(),1))
        self.music_volume_txt = self.font_2.render(self.music_volume_string, 1 ,pygame.Color('Red'))
    def update_option_menu_button_rect(self):
        for button in self.buttons:
            button.rect.width = (button.rect.width * self.res_scale)/ self.prev_res_scale
            button.rect.height = (button.rect.height * self.res_scale)/ self.prev_res_scale
    
    def change_res(self):
        if self.fullscreen_checkbox.state == True:
            self.window = pygame.display.set_mode(self.RESOLUTIONS[self.selected_resolution],pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(self.RESOLUTIONS[self.selected_resolution],pygame.RESIZABLE)
    
    def options_menu(self):
        game_menu:bool = True
        anim_index:int = 0
        BACKGROUND_ANIM:list[pygame.Surface] = self.ASSETS["MENU_FRAMES"]
        MAIN_MENU_ANIM_COOLDOWN:float =0.09
        update_time_m = self.get_time()
        change = False
        VOLUME_VALUE = 0.1

        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == KEYDOWN:
                    if event.key == K_r:
                        change = not change
                        if change:
                            self.window = pygame.display.set_mode(self.MONITOR_RESOLUTION,pygame.FULLSCREEN)
                        else:
                            self.window = pygame.display.set_mode(WINDOW_SIZE,pygame.RESIZABLE)

            #All Updates
            if self.music_check_box.check_clicked():
                if self.music_check_box.state == False:
                    pygame.mixer.music.stop()
                else:
                    pygame.mixer.music.play(loops = -1)
            
            if self.back_button.check_click():
                self.play_click_sound()
                return None
            
            if self.left_arrow.check_click():
                if self.selected_resolution != 0:
                    self.selected_resolution -= 1
                    self.prev_res_scale = self.res_scale
                    self.change_scale()
                    self.change_res()
                    self.update_option_menu_button_rect()
                    

            if self.right_arrow.check_click():
                if self.selected_resolution != len(self.RESOLUTIONS) - 1:
                    self.selected_resolution += 1
                    self.prev_res_scale = self.res_scale
                    self.change_scale()
                    self.change_res()
                    self.update_option_menu_button_rect()

            if self.fps_arrow.check_click():
                if self.selected_fps >= len(self.POSSIBLE_FPS) - 1:
                    self.selected_fps = 0
                else:
                    self.selected_fps += 1
                
                self.Fps = self.POSSIBLE_FPS[self.selected_fps]
            
            if self.fullscreen_checkbox.check_clicked():
                if self.fullscreen_checkbox.state == False:
                    pygame.display.set_mode(self.RESOLUTIONS[self.selected_resolution],pygame.RESIZABLE)

                else:
                    pygame.display.set_mode(self.RESOLUTIONS[self.selected_resolution],pygame.FULLSCREEN)

            if self.left_music_volume_arrow.check_click():
                if pygame.mixer.music.get_volume() >= 0.1:
                    pygame.mixer.music.set_volume(round(pygame.mixer.music.get_volume(),1) - VOLUME_VALUE)
                else:
                    pygame.mixer.music.set_volume(0)

            if self.right_music_volume_arrow.check_click():
                if pygame.mixer.music.get_volume() <= 1:
                    pygame.mixer.music.set_volume(round(pygame.mixer.music.get_volume(),1) + VOLUME_VALUE)
                else:
                    pygame.mixer.music.set_volume(1)

            self.update_text()

            # All Draws
            #print(self.res_scale)
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))

            self.display.blit(self.GAME_TITLE_IMG,(5,5))
            
            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))

            self.window.blit(self.music_txt, (10 * self.res_scale, self.res_scale * 135))
            self.window.blit(self.resolution_txt, (180 * self.res_scale, self.res_scale * 127))
            self.window.blit(self.fps_txt,(10 * self.res_scale, self.res_scale * 165))
            self.window.blit(self.fullscreen_txt,(10 * self.res_scale, 210 * self.res_scale))
            self.window.blit(self.music_volume_txt,(10 * self.res_scale, 235 * self.res_scale))

            self.music_check_box.draw(self.window, 100 * self.res_scale, 120 * self.res_scale,0.5 * self.res_scale)
            self.back_button.draw(self.window, 10 * self.res_scale, 310 * self.res_scale, 0.5 * self.res_scale)
            self.left_arrow.draw(self.window,150 * self.res_scale, 130 * self.res_scale,0.25 * self.res_scale)
            self.right_arrow.draw(self.window, 325 * self.res_scale , 130 * self.res_scale, 0.25 * self.res_scale)
            self.fps_arrow.draw(self.window, 160 * self.res_scale, 170 * self.res_scale, 0.25 * self.res_scale)
            self.fullscreen_checkbox.draw(self.window,155 * self.res_scale, 194 * self.res_scale, 0.5 * self.res_scale)
            self.left_music_volume_arrow.draw(self.window, 270 * self.res_scale, 240 * self.res_scale, 0.25 * self.res_scale)
            self.right_music_volume_arrow.draw(self.window,300 * self.res_scale, 240 * self.res_scale, 0.25 * self.res_scale)
            


            pygame.display.update()
            self.clock.tick(self.Fps)
            
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
        

        # Menu_Loop
        while game_menu:
            #Events: Pygame input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            #All Updates
            if self.LEVEL_1.check_click() :
                self.play_click_sound()
                return 1
            if self.LEVEL_2.check_click():
                self.play_click_sound()
                return 2
            if self.LEVEL_3.check_click():
                self.play_click_sound()
                return 3
            if self.LEVEL_4.check_click():
                self.play_click_sound()
                return 4
            if self.LEVEL_5.check_click():
                self.play_click_sound()
                return 5
            
            
            # All Draws
            self.display.blit(pygame.transform.scale(BACKGROUND_ANIM[anim_index], DISPLAY_SIZE), (0, 0))

            
            
            self.window.blit(pygame.transform.scale(self.display, self.window.get_size()), (0, 0))

            self.window.blit(pygame.transform.scale(self.GAME_TITLE_IMG,(100 * self.res_scale,50 * self.res_scale)),
                             (5 * self.res_scale,5 * self.res_scale))
            
            self.LEVEL_1.draw(self.window,110 * self.res_scale,10 * self.res_scale,0.4 * self.res_scale)
            self.LEVEL_2.draw(self.window,190 * self.res_scale, 10* self.res_scale, 0.4* self.res_scale)
            self.LEVEL_3.draw(self.window,270* self.res_scale,10* self.res_scale,0.4* self.res_scale)
            self.LEVEL_4.draw(self.window,350* self.res_scale,10* self.res_scale,0.4* self.res_scale)
            self.LEVEL_5.draw(self.window,110* self.res_scale, 60* self.res_scale,0.4* self.res_scale)
            
            
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
            ##############################Selecting retry without clicking the button
            keys = pygame.key.get_pressed()

            if keys[K_SPACE]:
                self.playing = False
            #############################
            if self.retry_b.check_click():
                self.play_click_sound()
                self.playing = False
            if self.quit_b_dead_menu.check_click():
                self.play_click_sound()
                self.playing = False
                self.retry_game = False

            

    def dead_menu_draw(self):
        if self.player.dead:
            pygame.draw.rect(self.window, (255, 120, 219),
                             pygame.Rect(150* self.res_scale, 30* self.res_scale,
                                          300* self.res_scale, 300* self.res_scale), 0, 3)
            self.window.blit(self.dead_mesage_txt, (80* self.res_scale, 60* self.res_scale))
            self.retry_b.draw(self.window,270* self.res_scale, 120* self.res_scale, 0.5* self.res_scale)
            self.quit_b_dead_menu.draw(self.window,270* self.res_scale, 180* self.res_scale, 0.5* self.res_scale)
    #Draw's the entire pause screen(SE)
    def pause_screen_draw(self):
        if self.game_pause:
            pygame.draw.rect(self.window, (255, 120, 219),
                             pygame.Rect(150* self.res_scale, 30* self.res_scale, 
                                         300* self.res_scale, 300* self.res_scale), 0, 3)
            
            self.window.blit(self.pause_text,(230* self.res_scale,10* self.res_scale))
            
            self.quit_b_pause.draw(self.window,270* self.res_scale, 180* self.res_scale , 0.5 * self.res_scale)
            self.retry_b_pause.draw(self.window,270* self.res_scale, 120* self.res_scale, 0.5* self.res_scale)

    def draw_win_menu(self):
        if self.win:
            pygame.draw.rect(self.window, (255, 120, 219),
                             pygame.Rect(150* self.res_scale, 30* self.res_scale,
                                          300* self.res_scale, 300* self.res_scale), 0, 3)
            self.window.blit(self.win_message_txt, (80* self.res_scale, 60* self.res_scale))
            self.next_level_arrow.draw(self.window, 270*self.res_scale, 120*self.res_scale, 0.5 * self.res_scale)
            self.quit_win_menu.draw(self.window,270* self.res_scale, 180* self.res_scale , 0.5 * self.res_scale)
    
    def win_menu_logic(self):
        if self.win:
            ##############################Selecting retry without clicking the button
            keys = pygame.key.get_pressed()

            if keys[K_SPACE]:
                self.play_click_sound() 
                self.playing = False
                self.retry_game = False
                if (self.current_lvl+1) != 6:
                    self.new_game(self.current_lvl+1)
            #############################
            if self.next_level_arrow.check_click():
                self.play_click_sound() 
                self.playing = False
                self.retry_game = False
                if (self.current_lvl+1) != 6:
                    self.new_game(self.current_lvl+1)
            if self.quit_win_menu.check_click():
                self.play_click_sound() 
                self.playing = False
                self.retry_game = False
                


    def get_resolutions(self):
        self.RESOLUTIONS = []
        self.resolution_scales = [0.5]
        run:bool = True
        i = 1
        while run:
            new_resolution = (DISPLAY_SIZE[0] * i , DISPLAY_SIZE[1] * i)
            if (new_resolution[0] < self.MONITOR_RESOLUTION[0]) and (new_resolution[1] < self.MONITOR_RESOLUTION[1]):
                self.RESOLUTIONS.append(new_resolution)
                i+= 1
            else:
                for n in range(1,i-1):
                    if n == 2:
                        self.resolution_scales.append(1.5)
                    else:
                        self.resolution_scales.append(n)
                self.RESOLUTIONS.append(self.MONITOR_RESOLUTION)
                self.resolution_scales.append(2)
                run = False

    #Updates the logic of all the buttons that appear in the pause menu(SE) 
    def pause_screen_logic(self):
        if self.game_pause:
            ##############################Selecting retry without clicking the button
            keys = pygame.key.get_pressed()

            if keys[K_SPACE]:
                self.playing = False
            #############################
            if self.quit_b_pause.check_click():
                self.play_click_sound()
                self.playing = False
                self.retry_game = False
            if self.retry_b_pause.check_click():
                self.play_click_sound()
                self.playing = False


    #Debug functions
    def debug(self):
        #self.camera.show_thresholds(self.window)
        self.window.blit(self.update_fps(),(10,10))
        #self.window.blit(self.show_playerMoveVector(),(10,30))
        self.window.blit(self.show_DeltaTime(),(10,50))
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
        font = pygame.font.SysFont("Arial",int(18 * self.res_scale))
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
        music_names = ["01 Blossom Tree.wav","03 Himawari No Sato.wav","04 Whispering Stars.wav",
                       "06 Tengu.wav","07 Gion District.wav","08 Higanbana Field.wav",]
        music_paths = []

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
        #0:player_jump 1:player_walking 2:shooting 3:sword_hit_enemy 4:sword slash 5: player killed sound
        # 6:click_sound 7:deflect bullet sound 
        for q in range(nb_sounds):
            sounds.append(pygame.mixer.Sound(os.path.join("sounds",f'{q}.wav')))

        for name in music_names:
            music_paths.append(os.path.join("music", name))

        


        self.ASSETS["BOTONES_IMGS"] = botones_images
        self.ASSETS["MENU_FRAMES"] = menu_images
        self.ASSETS["BG_LAYERS"] = bg_layers
        self.ASSETS["TILES"] = tiles
        self.ASSETS["SFX"] = sounds 
        self.ASSETS["MUSIC_PATHS"] = music_paths
    
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
sys.exit(0)

