import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game_attritues, spawn_pos:tuple, map_width:int, TRH_A:int, TRH_B:int):
        self.groups = game_attritues.all_sprites, game_attritues.player_group , game_attritues.player_and_tiles
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
        self.PLAYER_ANIMATION_COOLDOWN = [80,50,125,70]
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
        self.TRESHOLD_A = TRH_A
        self.TRESHOLD_B = TRH_B


        # Other player attributes
        self.map_width = map_width
        self.dead = False
        self.attack = False
        self.attacking = False
        self.attack_sprite_object = None

        self.x = spawn_pos[0] * TILE_SIZE
        self.y = spawn_pos[1] * TILE_SIZE


    #Updates player logic every frame(SE)
    def update(self, frame_x:int, frame_right:int):
        #print(self.attack)
        self.Jump_Queue()
        self.get_input()
        self.apply_gravity()
        self.check_no_longer_jumping()
        self.stop_player_motion(frame_x, frame_right)
        self.move()
        self.coyote_time()
        self.jump_buffer()
        self.update_animation()
        self.perform_attack()
        
        
    #Moves the player to the coordinates  the velocity vector points at(SE)
    def move(self):
        self.x += self.velocity.x * self.game.dt
        self.y += self.velocity.y * self.game.dt
        self.rect.x =  round(self.x)
        self.check_collision_with_tile('x')
        self.rect.y = round(self.y)
        self.check_collision_with_tile('y')
    
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
    #Also checks if the player is on the ground
    #->param dir should only be 'y' or 'x'
    def check_collision_with_tile(self, dir:str):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self,self.game.all_tiles,False)
            if hits:
                if self.velocity.x > 0:#Moving to the right when collided
                    self.x = hits[0].rect.left - self.rect.width
                if self.velocity.x < 0:#Moving to the left when collided
                    self.x = hits[0].rect.right
                if self.velocity.x == 0 and self.rect.right >= self.TRESHOLD_B:#When moving to the right and beyond treshold B
                    self.x = hits[0].rect.left - self.rect.width 
                if self.velocity.x == 0 and self.rect.left <= self.TRESHOLD_A:#When moving to the left and beyond treshold A
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

    def perform_attack(self):
        if self.attack and self.flip:
            return AttackSprite(self.game, "left")
            
        if self.attack and not self.flip:
            return AttackSprite(self.game, "right")
            

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
    def stop_player_motion(self, frame_x:int, frame_right:int):
        if not self.camera_locked(frame_x, frame_right):
            if self.rect.left <= self.TRESHOLD_A and self.velocity.x < 0:
                self.velocity.x = 0
            if self.rect.right >= self.TRESHOLD_B and self.velocity.x > 0:
                self.velocity.x = 0
        else:
            pass
    
    
    #Checks if the camera is locked(not moving)
    #->param frame_x an interger representing the x position of the camera(topleft corner of the frame)
    #->param frame_right an interger representing the x position of the righ side of the camera frame
    #->param map_pixel_width an integer indicating the maps pixel width
    #->returns true if frame_x is equal or inferior to 0 or if the right side of the camera frame is equal or superior to the map
    #          pixel width else false
    def camera_locked(self,frame_x:int, frame_right:int):
        if frame_x <= 0 or frame_right >= self.map_width:
            return True
        return False

    #Handles animation logic (SE)
    #Changing animation frame & reseting animation when it's done 
    # & changing the  animation depending on the action
    #Also changes the attacking variable so that the program can know if the attack animation is still playing
    def update_animation(self):
        
        # update img depending on current frame
        self.image = self.animation_list[self.action][self.index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.PLAYER_ANIMATION_COOLDOWN[self.action]:
            self.update_time = pygame.time.get_ticks()
            self.index += 1

            # if the animation has run out , reset back to the start
            if self.index >= len(self.animation_list[self.action]):
                self.index = 0
                if self.action == 3:#when the attack animations stops the 'attack' variable needs to be set to False again
                    self.attack = False


        #Changes action
        if not self.dead:
            if self.velocity.y < 0:
                self.attack = False
                self.update_action(2)  # 2:Jump

            elif self.moving_right or self.moving_left:
                self.attack = False
                self.update_action(1)  # 1:run
            
            elif self.attack:
                self.update_action(3)   #3:attack

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
        
    #Calculates the right coordinates for the current player image to be showned so that it's inside the player rect
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
    def __init__(self,game_attributes ,spawn_pos:tuple):
        self.groups = game_attributes.all_sprites, game_attributes.all_enemies
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game = game_attributes
        
        #Enemy animtion stuff
        self.ANIMATION_TYPES:list[str] = ["idle","run"]
        self.ENEMY_STATES :list[str] = ["idle", "attacking"]
        self.animation_list = self.load_enemy_assets()
        self.anim_index = 0
        self.anim_action = 0 
        self.image = self.animation_list[self.anim_action][self.anim_index]
        self.rect = pygame.Rect((100,0), (13, 16))#100 to fix a bullet spawning bug
        self.flip = False
        self.ENEMY_ANIMATION_COOLDOWN = 125
        self.SHOOTING_COOLDOWN = 230
        self.update_time = pygame.time.get_ticks()
        self.shooting_update_time = pygame.time.get_ticks()

        #Enemy movement stuff
        self.velocity  = pygame.math.Vector2(0,0) 
        self.speed = 100
        self.moving_right = False
        self.moving_left = False
        self.gravity = 830
        self.enemy_clock = 0
        self.on_ground = True
        self.jumping = False

        # Other player attributes
        self.dead = False
        self.VISION_RANGE = 100
        self.state:str = self.ENEMY_STATES[0]
        self.player_is_to_the_right = False
        self.player_is_to_the_left = False
        self.attacking = False

        self.x = spawn_pos[0] * TILE_SIZE
        self.y = spawn_pos[1] * TILE_SIZE
    
    #Updates the enemy logic every frame(SE)
    def update(self):
        self.enemy_AI()
        self.apply_gravity()
        self.move_enemy()
        self.update_animation()
        self.enemy_clock += 1 * self.game.dt
        if self.enemy_clock >= 3:
            self.enemy_clock = 0
        
        
    #Determines whether if  the enemy is idle or attacking the player(SE)
    def decide_enemy_state(self):
        if self.player_in_range():
            self.state = self.ENEMY_STATES[1]
        else:
            self.state = self.ENEMY_STATES[0]
        
    #Checks if the player is inside the range of vision of the enemy
    def player_in_range(self):
        player_rect_left = (self.game.player.rect.left <= self.rect.centerx + self.VISION_RANGE) and (self.game.player.rect.left >= self.rect.centerx - self.VISION_RANGE)
        player_rect_right = (self.game.player.rect.right >= self.rect.centerx - self.VISION_RANGE) and (self.game.player.rect.right <= self.rect.centerx + self.VISION_RANGE)
        player_rect_bottom = self.game.player.rect.bottom >= self.rect.top
    
        player_in_range_bool = (player_rect_left or player_rect_right) and player_rect_bottom
        if player_in_range_bool:
            return True
        else:
            return False            
    
    #Apply's gravity to the enemy(SE)
    def apply_gravity(self):
        self.velocity.y += self.gravity * self.game.dt
        if self.velocity.y > 1500:
            self.velocity.y = 1500
    
    #Decides the actions  the enemy is gonna perform(attacking,moving idly)(SE)
    def enemy_AI(self):
        self.decide_enemy_state()
        self.player_is_to_the_right = self.game.player.rect.right >= self.rect.centerx #True if player is to the right of the enemy
        self.player_is_to_the_left =  self.game.player.rect.right <= self.rect.centerx #True if player is to the left of the enemy
        
        if self.state == self.ENEMY_STATES[0]:#idle:
            if self.enemy_clock < 2:#standing still
                self.stay_still()
            if self.enemy_clock > 2 and self.enemy_clock < 2.5:# moving right
                self.move_right()
            if self.enemy_clock > 2.5 and self.enemy_clock < 3:# moving left
                self.move_left()
        if self.state == self.ENEMY_STATES[1]:#attacking
            self.stay_still()
            if self.player_is_to_the_right:
                self.flip = True
                if pygame.time.get_ticks() - self.shooting_update_time > self.SHOOTING_COOLDOWN:
                    self.shooting_update_time = pygame.time.get_ticks()
                    self.attacking = True
            if self.player_is_to_the_left:
                self.flip = False
                if pygame.time.get_ticks() - self.shooting_update_time > self.SHOOTING_COOLDOWN:
                    self.shooting_update_time = pygame.time.get_ticks()
                    self.attacking = True

        
        if self.moving_left:
            self.velocity.x = -self.speed
            self.flip = False

        elif self.moving_right:
            self.velocity.x = self.speed
            self.flip = True   
        else:
            self.velocity.x = 0

    #Makes the enemy stay still(SE)
    #This fucntion should be used inside the enemy_AI function
    def stay_still(self):
        self.moving_left = False
        self.moving_right = False
    
    #Makes the enemy move to the right(SE)
    #This fucntion should be used inside the enemy_AI function
    def move_right(self):
        self.moving_right = True
        self.moving_left = False
    #Makes the enemy move to the left(SE)
    #This fucntion should be used inside the enemy_AI function
    def move_left(self):
        self.moving_left = True
        self.moving_right = False
    
    #Moves the enemy to the coordinates  the velocity vector points at(SE)
    def move_enemy(self):
        self.x += self.velocity.x * self.game.dt + self.game.camera.scroll_amount
        self.y += self.velocity.y * self.game.dt
        self.rect.x =  round(self.x)
        self.check_collision_with_tile('x')
        self.rect.y = round(self.y)
        self.check_collision_with_tile('y')
    
    #Checks for collisions in the  y or x direction and positions the enemy accordingly(SE)
    #Also checks if the enemy is on the ground
    #->param dir should only be 'y' or 'x'
    def check_collision_with_tile(self, dir:str):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(self,self.game.all_tiles,False)
            if hits:
                if self.velocity.x > 0:#Moving to the right when collided
                    self.x = hits[0].rect.left - self.rect.width
                if self.velocity.x < 0:#Moving to the left when collided
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

    #Checks if the enemy is no longer on the ground(SE)
    #enemy not on ground <-->  14.8 < velocity.y or velocity.y < 0 (because of velocity bug)
    def check_not_on_ground(self):
        if self.velocity.y > 27 or self.velocity.y < 0: #14.7 --> 60fps|| 27 --> unlocked fps
            self.on_ground = False
            #print(self.velocity.y)
    
    #Makes the enemy shoot
    #-> returns a Bullet object set to a position depending on the position of the player(player is to the left or to the right?)
    def attack(self):
        if self.attacking:
            if self.player_is_to_the_left:
                self.attacking = False
                return Bullet(self.game, self.rect.midleft,-1)
            elif self.player_is_to_the_right:
                self.attacking = False
                return Bullet(self.game, self.rect.midright,1)
            else:
                return None

    def draw(self, display:pygame.Surface):
        display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x,self.rect.y))
        if self.game.debug_on:
            pygame.draw.rect(display, (0,0,255), self.rect, 1)
            display.blit(pygame.Surface((5,5)),(self.rect.centerx + self.VISION_RANGE, self.rect.y))
            display.blit(pygame.Surface((5,5)),(self.rect.centerx - self.VISION_RANGE, self.rect.y))
    #Handles animation logic (SE)
    #Changing animation frame & reseting animation when it's done 
    # & changing the  animation depending on the action
    def update_animation(self):
        
        # update img depending on current frame
        self.image = self.animation_list[self.anim_action][self.anim_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > self.ENEMY_ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.anim_index += 1

            # if the animation has run out , reset back to the start
            if self.anim_index >= len(self.animation_list[self.anim_action]):
                self.anim_index = 0

        #Changes action
        if not self.dead:
            if self.state == self.ANIMATION_TYPES[1]:
                self.update_action(1)  # 1:run

            else:
                self.update_action(0)  # 0:idle

    #Changes player's current action to the next action
    def update_action(self, new_action:int):

        # check if new action is different to the previous
        if new_action != self.anim_action:
            self.anim_action = new_action
            # update the anim settings
            self.anim_index = 0
            self.update_time = self.game.dt

    #Loads the enemy assets(SE)
    def load_enemy_assets(self):
        animation_list = []
        for animation in self.ANIMATION_TYPES:
            temp_list = []
            
            num_of_frames = len(os.listdir(f'images/enemy_imgs/{animation}'))
            for i in range(num_of_frames):
                e_img = pygame.transform.scale_by(pygame.image.load(os.path.join("images", "enemy_imgs", animation, f'{i}.png')),1.5)
                temp_list.append(e_img)
            animation_list.append(temp_list)
        return animation_list

class Tile(pygame.sprite.Sprite):
    def __init__(self, game_attributes, image:pygame.Surface, spawn_pos:tuple):
        self.groups = game_attributes.all_sprites, game_attributes.all_tiles, game_attributes.player_and_tiles
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game_attributes, spawn_pos:tuple , direction:int):
        self.groups = game_attributes.all_sprites, game_attributes.all_bullets
        #The class constructor (__init__ method) takes an argument of a Group (or list of Groups) the Sprite instance should belong to. 
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game = game_attributes
        self.image = pygame.Surface((3,2))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.BULLET_SPEED = 300
        self.velocity = pygame.math.Vector2(0,0)
        self.velocity.x = direction * self.BULLET_SPEED
        self.x:float = spawn_pos[0]
        self.y:float = spawn_pos[1]

    #Updates the bullet Logic
    def update(self):
        self.x += self.velocity.x * self.game.dt + self.game.camera.scroll_amount
        self.rect.x = round(self.x)
        self.rect.y = self.y
        self.check_for_collision()
    
    #Removes the bullet from all sprite groups the bullet is part of if the bullet collides with the player, a tile,
    #or if the player's attack sprite hits the bullet(SE) 
    def check_for_collision(self):
        hits = pygame.sprite.spritecollideany(self,self.game.player_and_tiles)
        attack_hits = pygame.sprite.spritecollideany(self,self.game.attack_sprite)
        if hits or attack_hits:
            self.kill()
    
    def draw(self,display):
        display.blit(self.image,(self.rect.x,self.rect.y ))

class AttackSprite(pygame.sprite.Sprite):
    def __init__(self, game_attributes, direction:str):
        self.groups = game_attributes.attack_sprite
        #The class constructor (__init__ method) takes an argument of a Group (or list of Groups) the Sprite instance should belong to.
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.game = game_attributes
        self.image = pygame.Surface((5,10))
        self.image.fill((0,255,0))
        self.dir = direction
        self.rect = self.set_rect_direction(direction)
    
    #Sets the direction in which the attack rect is gonna spawn(left or right)
    #-> param dir a String that indicates a direction ("left" or "right")
    #-> returns a Rect object thats either gonna be to the left or the right of the player depending on the direction
    def set_rect_direction(self,dir):
        if dir == "left":
            return self.image.get_rect(right = self.game.player.rect.left)
        elif dir == "right":
            return self.image.get_rect(left = self.game.player.rect.right)
    
    #Updates the attackSprite Logic(SE)
    def update(self):
        if self.dir == "left":
            self.rect.right = self.game.player.rect.left
        elif self.dir == "right":
            self.rect.left = self.game.player.rect.right
        self.rect.y = self.game.player.rect.y

        if not self.game.player.attack:
            self.kill()