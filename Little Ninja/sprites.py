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
        
        #Player Movement attributes
        self.velocity  = pygame.math.Vector2(0,0) 
        self.y_current_value = 0
        self.speed = 215
        self.moving_right = False
        self.moving_left = False
        self.jump_intensity = -300
        self.jumping = False
        self.gravity = 830
        self.air_timer = 0

        self.x = spawn_pos[0] * TILE_SIZE
        self.y = spawn_pos[1] * TILE_SIZE


    #Player's logic related methods(SE)
    def update(self):
        self.get_input()
        self.apply_gravity()
        self.move()
        
        
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
        #self.velocity.x = 0 

        if self.moving_left:
            self.velocity.x = -self.speed
            self.flip = True
        

        elif self.moving_right:
            self.velocity.x = self.speed
            self.flip = False   
        else:
            self.velocity.x = 0      

    def check_collision_with_tile(self, dir):
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
                    if (self.rect.centery - hits[0].rect.centery) > 0:
                        self.velocity.y = 0
                if self.velocity.y < 0:#Moving up when collided
                    self.y = hits[0].rect.bottom
                    if (self.rect.centery - hits[0].rect.centery) < 0:
                        self.velocity.y = 0
                self.rect.y = self.y 
    
    def jump(self):
            self.velocity.y = self.jump_intensity

    def apply_gravity(self):
        self.velocity.y += self.gravity * self.game.dt
        if self.velocity.y > 1500:
            self.velocity.y = 1500

    
    #Player's rendering related methods
    def draw(self, display):
        display.blit(pygame.transform.flip(self.image,self.flip,False), (self.rect.x, self.rect.y))
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
