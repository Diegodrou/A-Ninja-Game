from turtle import window_height
import pygame
import os

from settings import WINDOW_SIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.dead = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.flip = False
        self.current_x = 0
        self.window_height = WINDOW_SIZE[1]
        #load idle anim frames/action 0
        animation_types = ['idle', 'run', 'jump']
        for animation in animation_types:
        # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'assets/img/{animation}'))
            for i in range(num_of_frames):
                p_img = pygame.image.load(os.path.join("assets","img",animation, f'{i}.png'))
                temp_list.append(p_img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect(topleft = pos)
        self.width =self.image.get_width()
        self.height = self.image.get_height()
       
       #Player movement attributes
        self.jump_intensity = -6
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 2
        self.moving_right = False
        self.moving_left = False
        self.gravity = 0.3
        self.air_timer = 0

        #debug atributes
        self.t_rect = False
    
    def movementANDcollisions(self,tile_rects):
        #Reset movement variables
        dx = 0
        dy = 0
        #gets inputs and the values that represent how much the player is gonna move
        if self.moving_left:
            self.direction.x = -1
            dx = self.direction.x *self.speed
            self.flip = True
        if self.moving_right :
            self.direction.x = 1
            dx = self.direction.x * self.speed
            self.flip = False

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
        #update player postion
        self.rect.x += dx
        self.rect.y += dy 

        if self.rect.centerx > 210 and self.direction.x > 0:
            self.rect.x -= dx 
            screen_scroll = -dx
        elif self.rect.centerx < 50 and self.direction.x < 0:
            self.rect.x -= dx
            screen_scroll = -dx
        else:
            screen_scroll = 0 
        return screen_scroll     
        #if self.collision_types['bottom']:
           #self.air_timer = 0
        #else:
            #self.air_timer += 1

    def get_input(self):
        
        if self.moving_right == True:
            self.flip = False
            self.direction.x = 1
            
            
        elif self.moving_left == True:
            self.flip = True
            self.direction.x  = -1
            
        else:
            self.direction.x = 0
    
                
    def apply_gravity(self):  
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
        #self.y += self.direction.y
        if self.direction.y > 5:
            self.direction.y = 5

    def jump(self):
            self.direction.y = self.jump_intensity
             
    def update(self):
        self.update_anim()
        self.check_dead() 
        
    def update_anim(self):

        #update animation
        ANIMATION_COOLDOWN = 150
        #update img depending on current frame
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
            if self.direction.y < 0:
                self.update_action(2)#2:Jump

            elif self.moving_right or self.moving_left:
                    self.update_action(1)#1:run
            else:
                    self.update_action(0)#0:idle


    def update_action(self, new_action):
        
        #check if new action is different to the previous
        if new_action != self.action:
            self.action = new_action
            #update the anim settings
            self.index = 0
            self.update_time = pygame.time.get_ticks()
    
    def check_dead(self):
        if self.rect.y > self.window_height:
            self.dead = True
        else:
            self.dead = False 

    def draw(self,display):
        display.blit(pygame.transform.flip(self.image,self.flip,False), self.rect)
        if self.t_rect:
            pygame.draw.rect(display, (255,0,0), self.rect,  1)