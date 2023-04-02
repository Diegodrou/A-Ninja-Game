import pygame
import os
from Bullet import Bullet

from settings import WINDOW_SIZE

left_threshold = 80
right_threshold = 90

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.dead = False
        self.flip = False
        self.speed = 1
        self.direction = pygame.math.Vector2(0,0)
        self.direction.x = -1
        self.moving_right = False
        self.moving_left = False
        self.move_counter = 0
        self.gravity = 0.3
        self.idle_state = True
        self.attack_state = False
        self.Shoot = False
        self.debug = False
        self.update_time = pygame.time.get_ticks()

        #Animation related stuff
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #load idle anim frames/action 0
        animation_types = ['run']
        for animation in animation_types:
        # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'assets/enemyAssets/{animation}'))
            for i in range(num_of_frames):
                p_img = pygame.image.load(os.path.join("assets","enemyAssets",animation, f'{i}.png'))
                temp_list.append(p_img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect(topleft = pos)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def movementANDcollisions(self,tile_rects): #moves the player and cheks for  collisions
        #Reset movement variables
        dx = 0
        dy = 0
        #gets inputs and the values that represent how much the player is gonna move
        
        if self.moving_left:
            dx = self.direction.x *self.speed
            self.flip = False
        if self.moving_right :
            dx = self.direction.x * self.speed
            self.flip = True
        if self.attack_state:
            dx = 0

        
        #Apply gravity
        self.direction.y += self.gravity
        if self.direction.y > 5:
            self.direction.y = 5
        dy += self.direction.y    
        

        #Check for collisions
        for tile in tile_rects:
            #Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y,self.width, self.height):
                dx = 0
            #Check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy,self.width, self.height):
                #check if below ground i.e. jumping(ceiling collision)
                if self.direction.y < 0:
                    self.direction.y = 0
                    dy = tile[1].bottom - self.rect.top

                #check if above the ground i.e falling (ground collision)
                elif self.direction.y >= 0:
                   self.direction.y = 0
                   dy = tile[1].top - self.rect.bottom
                   self.air_timer = 0 
        #update enemy postion
        self.rect.x += dx
        self.rect.y += dy 

    def AI(self,player_rect,player_status,tile_rects,screen_scroll):
        if (not self.dead) and not player_status:
            self.decide_enemy_state(player_rect)
            if self.idle_state:
                if self.direction.x == -1:
                    self.moving_left = True
                else:
                    self.moving_left = False
                self.moving_right = not self.moving_left
                self.movementANDcollisions(tile_rects)
                self.move_counter += 1
                
                if self.move_counter > 16:
                    self.direction.x *= -1
                    self.move_counter *= -1
            if self.attack_state:
                SHOOTING_COOLDOWN = 500
                x_diff = self.rect.x - player_rect.x
                self.movementANDcollisions(tile_rects)
                if x_diff > 0: #check if player is at the left of the enemy
                    self.moving_left = True
                    self.direction.x = -1
                    self.moving_right = False
                if x_diff < 0:#check if player is at the right of the enemy
                    self.moving_right = True
                    self.direction.x = 1
                    self.moving_left = False
                
                
                if self.moving_left:
                    self.flip = False
                
                if self.moving_right:
                    self.flip = True
                if pygame.time.get_ticks() - self.update_time > SHOOTING_COOLDOWN:
                    self.update_time = pygame.time.get_ticks()
                    if not self.dead:
                        self.Shoot = True
                
        #scroll
        self.rect.x += screen_scroll


    def update_anim(self):

        #update animation
        ANIMATION_COOLDOWN = 150
        #update img depending on current frame
        if not self.attack_state:
            self.image = self.animation_list[self.action][self.index]
            #check if enough time has passed since the last update
            if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
                self.update_time = pygame.time.get_ticks()
                self.index += 1
                #if the animation has run out , reset back to the start
                if self.index >= len(self.animation_list[self.action]):
                    self.index = 0
            #changes actions
            if not self.dead:

                if self.moving_right or self.moving_left:
                        self.update_action(0)#0:run
        else:
            self.index = 0


    def update_action(self, new_action):
        
        #check if new action is different to the previous
        if new_action != self.action:
            self.action = new_action
            #update the anim settings
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_dead(self,players_attack_rect, player_hit):
        if players_attack_rect.colliderect(self.rect) and player_hit :
            self.dead = True
            self.kill()

    def decide_enemy_state(self,player_rect):
        if (player_rect.x <= (self.rect.x + right_threshold)) and (player_rect.x >= self.rect.x - left_threshold) and (player_rect.y >= self.rect.top - 5) and (player_rect.y < self.rect.bottom):
            self.idle_state =False
            self.attack_state = True
        else:
            self.attack_state = False
            self.idle_state = True
    
    def shoot(self):
        if self.moving_left:
            self.Shoot = False
            return Bullet(self.rect.midleft[0],self.rect.midleft[1],self.direction.x)
        if self.moving_right:
            self.Shoot = False
            return Bullet(self.rect.midright[0],self.rect.midright[1],self.direction.x)

        

    def update(self,attack_rect, player_hit):
        self.check_dead(attack_rect, player_hit)
        self.update_anim()

    def draw(self,display):
        display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x , self.rect.y))
        if self.debug:
            display.blit(pygame.Surface((5,5)),(self.rect.x + right_threshold, self.rect.y))
            display.blit(pygame.Surface((5,5)),(self.rect.x - left_threshold, self.rect.y))