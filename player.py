import pygame
import os

from settings import WINDOW_SIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.dead = False
        self.flip = False
        self.window_height = WINDOW_SIZE[1]
        self.ATTACK_RECT_W = 14
        self.ATTACK_RECT_W_WHEN_FLIPPED = -11 # when the frame is flipped the attack rect appears bigger if I only change the sign of the ATTACK_RECT_W .
                                              #In consequence I have to make it bit shorter when flipped.

        self.hit_counter = 0 #get the number of times that the attack collider collided with the enemy collider during the attack animation
        #animation related stuff
        self.animation_list = []
        self.index = 0
        self.action = 0
        self.attack = False
        self.hit_enemy = False
        self.update_time = pygame.time.get_ticks()
        #load idle anim frames/action 0
        animation_types = ['idle', 'run', 'jump','attack']
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
    
    def attacks(self,target):
        self.hit = False
        if self.flip:
            attack_rect = pygame.Rect(self.rect.centerx,self.rect.y, self.ATTACK_RECT_W_WHEN_FLIPPED ,self.rect.height)
        else:
            attack_rect = pygame.Rect(self.rect.centerx,self.rect.y, self.ATTACK_RECT_W,self.rect.height)
        if attack_rect.colliderect(target):
            if self.action == 3:#so that it doenst happen while other animations are running
                if self.hit_counter > 0:
                    pass
                else:
                    self.hit_counter += 1
                    print("hit")
                    self.hit_enemy = True
    


    def movementANDcollisions(self,tile_rects,enemy_rect):
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
         #attack inputs
        if self.attack:
            self.attacks(enemy_rect)
            #self.attack = False
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
        #if self.action == 1:
            #self.attack = False
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1
            #if the animation has run out , reset back to the start
            if self.index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.attack = False
                    self.hit_counter = 0
                #if self.action == 1:
                    #self.attack = False
                self.index = 0
        #changes actions
        if not self.dead:
            if self.direction.y < 0:
                self.update_action(2)#2:Jump

            elif self.moving_right or self.moving_left:
                    self.update_action(1)#1:run
            elif self.attack:
                self.update_action(3)#3:attack
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
        if self.flip and self.action == 1:
            display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x - 7 , self.rect.y))
        
        elif self.flip and self.action == 2:
            display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x - 7 , self.rect.y))

        elif self.flip and self.action == 3:
            display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x - 7 , self.rect.y))
        
        else:
            display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x , self.rect.y))
        if self.t_rect:
            pygame.draw.rect(display, (255,0,0), self.rect,  1)
            if self.flip:
                pygame.draw.rect(display, (0,255,0), pygame.Rect(self.rect.centerx,self.rect.y, self.ATTACK_RECT_W_WHEN_FLIPPED ,self.rect.height) ,  1)
            else :
                pygame.draw.rect(display, (0,255,0), pygame.Rect(self.rect.centerx,self.rect.y, self.ATTACK_RECT_W,self.rect.height) ,  1)