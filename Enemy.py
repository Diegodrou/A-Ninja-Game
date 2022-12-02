import pygame
import os

from settings import WINDOW_SIZE


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

    def AI(self,player_status,tile_rects,screen_scroll):
        if (not self.dead) and not player_status:
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

        #scroll
        self.rect.x += screen_scroll

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

            if self.moving_right or self.moving_left:
                    self.update_action(0)#0:run
 #           else:
 #                   self.update_action(0)#1:shooting

    def update_action(self, new_action):
        
        #check if new action is different to the previous
        if new_action != self.action:
            self.action = new_action
            #update the anim settings
            self.index = 0
            self.update_time = pygame.time.get_ticks()

    def check_dead(self):
        pass

    def update(self):
        self.update_anim()

    def draw(self,display):
        display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x , self.rect.y))