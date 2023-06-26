import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game_attritues, spawn_pos:tuple):
        self.groups = game_attritues.all_sprites
        #The class constructor (__init__ method) takes an argument of a Group (or list of Groups) the Sprite instance should belong to. 
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game = game_attritues
        #Player sprite and animation attributes
        self.ANIMATION_TYPES = ['idle', 'run', 'jump', 'attack']
        self.animation_list =  self.load_player_assets(self.ANIMATION_TYPES)
        self.index = 0
        self.action = 0
        self.image = self.animation_list[self.action][self.index]
        self.rect = pygame.Rect((0,0), (13, 16))
        self.flip = False
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.PLAYER_ANIMATION_COOLDOWN = 125
        self.update_time = pygame.time.get_ticks()
        
        #Player Movement attributes
        self.velocity  = pygame.math.Vector2(0,0) 
        self.speed = 215
        self.moving_right = False
        self.moving_left = False
        self.jump_intensity = -300
        self.jumping = False
        self.gravity = 830
        self.air_timer = 0
        self.on_ground = False
        self.jump_buffer_timer = 0
        self.jump_q = False
        self.Jkey_pressed = False
        self.JUMP_BUFFER_TRESHOLD = 0.6
        self.COYOTE_TIME_TRESHOLD = 0.11

        # Other player attributes
        self.dead = False

        self.x = spawn_pos[0] * TILE_SIZE
        self.y = spawn_pos[1] * TILE_SIZE


    #Updates player logic every frame(SE)
    def update(self,c_treshold_A, c_treshold_B):
        self.Jump_Queue()
        self.get_input()
        self.apply_gravity()
        self.check_no_longer_jumping()
        self.stop_player_motion(c_treshold_A,c_treshold_B)
        self.move(c_treshold_A, c_treshold_B)
        self.coyote_time()
        self.jump_buffer()
        self.update_animation()
        
        
    #Moves the player to the coordinates  the velocity vector points at(SE)
    def move(self,c_treshold_A, c_treshold_B):
        self.x += self.velocity.x * self.game.dt
        self.y += self.velocity.y * self.game.dt
        self.rect.x =  round(self.x)
        self.check_collision_with_tile('x', c_treshold_A, c_treshold_B)
        self.rect.y = round(self.y)
        self.check_collision_with_tile('y', c_treshold_A, c_treshold_B)
    
    #Checks for player input and sets velocity in the x axis accordingly(SE)
    def get_input(self):
        if self.moving_left:
            self.velocity.x = -self.speed
            self.flip = True

        elif self.moving_right:
            self.velocity.x = self.speed
            self.flip = False   
        else:
            self.velocity.x = 0      
    
    #Checks for collisions in the  y or x direction and positions the player accordingly(SE)
    #->param dir should only be 'y' or 'x'
    def check_collision_with_tile(self, dir:str, c_treshold_A, c_treshold_B):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self,self.game.all_tiles,False)
            if hits:
                if self.velocity.x > 0:#Moving to the right when collided
                    self.x = hits[0].rect.left - self.rect.width
                if self.velocity.x < 0:#Moving to the left when collided
                    self.x = hits[0].rect.right
                if self.velocity.x == 0 and self.rect.right >= c_treshold_B:#When moving to the right and beyond treshold B
                    self.x = hits[0].rect.left - self.rect.width 
                if self.velocity.x == 0 and self.rect.left <= c_treshold_A:#When moving to the left and beyond treshold A
                    self.x = hits[0].rect.right
                self.velocity.x = 0
                self.rect.x = self.x 
        if dir == 'y':
            hits = pygame.sprite.spritecollide(self,self.game.all_tiles,False)
            if hits:
                if self.velocity.y > 0:#Moving down when collided
                    self.y = hits[0].rect.top - self.rect.height
                    self.on_ground = True # on ground <--> colliding on the y axis & velocity.y > 0
                    self.jumping = False
                if self.velocity.y < 0:#Moving up when collided
                    self.y = hits[0].rect.bottom
                self.velocity.y = 0
                self.rect.y = self.y

            self.check_not_on_ground()


    #Checks if the player is no longer on the ground(SE)
    #ply not on ground <-->  14.8 < velocity.y or velocity.y < 0 (because of velocity bug)
    def check_not_on_ground(self):
        if self.velocity.y > 27 or self.velocity.y < 0: #14.7 --> 60fps|| 27 --> unlocked fps
            self.on_ground = False
            #print(self.velocity.y)
    
    #Makes the player jump(SE)
    def jump(self,jump):
        self.jumping = True
        if jump: 
            self.velocity.y = self.jump_intensity
    
    #Coyote time(SE)
    #A brief delay between an pressing the jump button and
    #the consequences of that action that has no physical cause and only exist for gameplay purposes
    #This function updates the air_timer
    def coyote_time(self):
        if self.on_ground:
            self.air_timer = 0
        else:
            self.air_timer += 1 * self.game.dt
    
    #jumpBuffer(SE)
    #This function updates the jumpBuffer timer
    def jump_buffer(self):
        if self.jumping:
            self.jump_buffer_timer = 0
        else:
            self.jump_buffer_timer += 1 * self.game.dt
    
    #Checks if the air timer surpassed the coyote time treshold
    def check_coyote_time(self):
        if self.air_timer < self.COYOTE_TIME_TRESHOLD:
            return True
        return False
    
    #Checks if the jumpBuffer timer surpassed the jumpBuffer threshold
    def check_jump_buffer(self):
        if self.Jkey_pressed and (self.jump_buffer_timer < self.JUMP_BUFFER_TRESHOLD):
            return True
        return False
    
    #Checks if the the player is no longer jumping and if so sets the jumping variable to false (SE)
    def check_no_longer_jumping(self):
        if self.velocity.y > 0 and self.jumping:
            self.jumping = False

    #Checks the different conditions in which a player should be allowed to jump
    # -->returns True if the player can jump , False if he can't jump
    def canJump(self):
        if self.on_ground  or self.check_coyote_time():
            return True
        return False
    
    #If there's a jump in the Jump queue and the player is on the ground a jump will be performed (SE)
    def Jump_Queue(self):
        self.jump_q = self.check_jump_buffer()
        if self.jump_q  and self.on_ground:
            self.jump(True)
            self.jump_q = False 
    
    #Apply's gravity to the player(SE)
    def apply_gravity(self):
        self.velocity.y += self.gravity * self.game.dt
        if self.velocity.y > 1500:
            self.velocity.y = 1500
    
    #Sets player x velocity to 0 if the left of the player rect is on treshold_A or
    #If the right of the player rect is on treshold_B(SE)
    def stop_player_motion(self, treshold_A:int, treshold_B:int):
        if self.rect.left <= treshold_A and self.velocity.x < 0:
            self.velocity.x = 0
        if self.rect.right >= treshold_B and self.velocity.x > 0:
            self.velocity.x = 0

    #Handles animation logic (SE)
    #Changing animation frame & reseting animation when it's done 
    # & changing the  animation depending on the action
    def update_animation(self):
        
        # update img depending on current frame
        self.image = self.animation_list[self.action][self.index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.PLAYER_ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

            # if the animation has run out , reset back to the start
            if self.index >= len(self.animation_list[self.action]):
                self.index = 0

        #Changes action
        if not self.dead:
            if self.velocity.y < 0:
                self.update_action(2)  # 2:Jump

            elif self.moving_right or self.moving_left:
                self.update_action(1)  # 1:run

            else:
                self.update_action(0)  # 0:idle

    #Changes player's current action to the next action
    def update_action(self, new_action:int):

        # check if new action is different to the previous
        if new_action != self.action:
            self.action = new_action
            # update the anim settings
            self.index = 0
            self.update_time = self.game.dt

    #Player's rendering related methods
    def draw(self, display:pygame.Surface):
        player_render_xy = self.find_blit_coordinates()
        display.blit(pygame.transform.flip(self.image,self.flip,False), player_render_xy)
        if self.game.debug_on:
            pygame.draw.rect(display, (255,0,0), self.rect, 1)
        
    
    def find_blit_coordinates(self):
            middle_of_current_surface = (self.image.get_width())/2
            middle_of_current_rect = self.rect.width/2
            distance_between_middles = middle_of_current_surface - middle_of_current_rect
            return (self.rect.x - distance_between_middles, self.rect.y)

    #Player's loading methods
    def load_player_assets(self,animation_types:list[str]):
        animation_list = []
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'images/player_imgs/{animation}'))
            for i in range(num_of_frames):
                p_img = pygame.image.load(os.path.join("images", "player_imgs", animation, f'{i}.png'))
                temp_list.append(p_img)
            animation_list.append(temp_list)
        return animation_list


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_position:tuple):
        pass

class Tile(pygame.sprite.Sprite):
    def __init__(self, game_attributes, image:pygame.Surface, spawn_pos:tuple):
        self.groups = game_attributes.all_sprites, game_attributes.all_tiles
        #The class constructor (__init__ method) takes an argument of a Group (or list of Groups) the Sprite instance should belong to. 
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.x = spawn_pos[0]
        self.y = spawn_pos[1]
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = spawn_pos[0] * TILE_SIZE
        self.rect.y = spawn_pos[1] * TILE_SIZE

    def draw(self,display):
        display.blit(self.image,(self.rect.x,self.rect.y ))
