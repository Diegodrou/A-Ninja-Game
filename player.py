from turtle import window_height
import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, pos,window_height):
        super().__init__()
        self.dead = False
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.flip = False
        self.current_x = 0
        self.window = window_height
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
        # self.rect = self.image.get_rect(topleft = pos)
        self.rect = pygame.rect.Rect(0, 0, 15, 15)
        self.collision_types =  {'top': False, 'bottom': False, 'right': False, 'left': False} # PEP8: spaces
        
        
        self.jump_count = 0
        self.jump_intensity = -6
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 2
        self.moving_right = False
        self.moving_left = False
        self.gravity = 0.3
        self.air_timer = 0

        #player status
        self.on_left = False
        self.on_right = False
        

        #debug atributes
        self.t_rect = True
    
    def movement_collision(self,tile_rects):
        #Horizontal movement
        self.rect.x += self.direction.x*self.speed
        
        for sprite in tile_rects.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left
                    self.collision_types['right'] = True
                    self.current_x = self.rect.right
                elif self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                    self.collision_types['left'] = True
                    self.current_x = self.rect.left

        if self.collision_types['right'] and (self.rect.right > self.current_x or self.direction.x <= 0):
            self.collision_types['right'] = False
        if self.collision_types['left'] and (self.rect.left < self.current_x or self.direction.x >= 0):
            self.collision_types['left'] = False

        #Vertical movement
        self.apply_gravity()

        for sprite in tile_rects.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.direction.y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.direction.y = 0
                    self.collision_types['bottom'] = True
                    
                elif self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
                    self.collision_types['top'] = True
        
        if self.collision_types['bottom'] and self.direction.y < 0 or self.direction.y > 1 :
            self.collision_types['bottom'] = False
        
        if self.collision_types['top'] and self.direction.y > 0:
            self.collision_types['top'] = False

        if self.collision_types['bottom']:
            self.air_timer = 0
        else:
            self.air_timer += 1

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
        if self.direction.y > 5:
            self.direction.y = 5

    def jump(self):
            self.direction.y = self.jump_intensity
             
    def update(self,tile_rects):
        self.get_input()
        self.movement_collision(tile_rects)
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
                self.update_action(2)

            elif self.moving_right or self.moving_left:
                    self.update_action(1)#1:run
            else:
                    self.update_action(0)#0:idle

        # #set rect
        # #for bottom collision
        # if self.collision_types['bottom'] and self.collision_types['right']:
        #     self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        # elif self.collision_types['bottom'] and self.collision_types['left']:
        #     self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        # elif self.collision_types['bottom']:
        #     self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        # #for top collisions
        # elif self.collision_types['top'] and self.collision_types['right']:
        #     self.rect = self.image.get_rect(topright = self.rect.topright)
        # elif self.collision_types['top'] and self.collision_types['left']:
        #     self.rect = self.image.get_rect(topleft = self.rect.topleft)
        # #elif self.collision_types['top']:
        # #    self.rect = self.image.get_rect(midtop = self.rect.midtop)
        # elif not self.collision_types['top'] and  not self.collision_types['bottom'] :
        #     self.rect = self.image.get_rect(center = self.rect.center)


    def update_action(self, new_action):
        
        #check if new action is different to the previous
        if new_action != self.action:
            self.action = new_action
            #update the anim settings
            self.index = 0
            self.update_time = pygame.time.get_ticks()
    
    def check_dead(self):
        if self.rect.y > self.window:
            self.dead = True
        else:
            self.dead = False 

    def draw(self,display):
        display.blit(pygame.transform.flip(self.image,self.flip,False),(self.rect.x,self.rect.y))
        if self.t_rect:
            pygame.draw.rect(display, (255,0,0), self.rect,  1)