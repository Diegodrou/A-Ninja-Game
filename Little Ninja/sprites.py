import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game_attritues, spawn_pos:tuple):
        self.groups = game_attritues.all_sprites
        #The class constructor (__init__ method) takes an argument of a Group (or list of Groups) the Sprite instance should belong to. 
        pygame.sprite.Sprite.__init__(self,self.groups)
        #Player sprite and animation attributes
        self.ANIMATION_TYPES = ['idle', 'run', 'jump', 'attack']
        self.animation_list =  self.load_player_assets(self.ANIMATION_TYPES)
        self.index = 0
        self.action = 0
        self.image = self.animation_list[self.action][self.index]
        self.rect = pygame.Rect(spawn_pos, (6, 16))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        
        #Player pos attributes
        self.pos = pygame.math.Vector2(spawn_pos[0],spawn_pos[1])

        #Player Movement attributes
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 2
        self.moving_right = False
        self.moving_left = False
        self.jump_intensity = -6
        self.gravity = 0.3
        self.air_timer = 0


    #Player's logic related methods
    def update(self):
        self.get_input()
        self.move()
        self.collisions()
    
    def move(self):
        pass
    
    def get_input(self):
        if self.moving_left:
            self.direction.x = -1

        if self.moving_right:
            self.direction.x = 1

    def collisions(self):
        pass
    
    #Player's rendering related methods
    def draw(self):
        pass
        

    
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

    def draw(self):
        pass
