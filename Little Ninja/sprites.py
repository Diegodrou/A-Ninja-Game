import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, start_position:tuple):
        
        #player sprite and animation attributes
        self.ANIMATION_TYPES = ['idle', 'run', 'jump', 'attack']
        self.animation_list =  self.load_player_assets(self.ANIMATION_TYPES)
        self.index = 0
        self.action = 0
        self.image = self.animation_list[self.action][self.index]
        self.rect = pygame.Rect(start_position, (6, 16))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        #Player Movement attributes
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 2
        self.moving_right = False
        self.moving_left = False
        self.jump_intensity = -6
        self.gravity = 0.3
        self.air_timer = 0

    def move(self):
        pass

    def update(self):
        pass

    def find_blit_coordinates(self):
        middle_of_current_surface = (self.image.get_width())/2
        middle_of_current_rect = self.rect.width/2
        distance_between_middles = middle_of_current_surface - middle_of_current_rect
        return (self.rect.x - distance_between_middles, self.rect.y)

    def draw(self):
        pass        

    
    def load_player_assets(self,animation_types:list[str]):
        animation_list = []
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'images/player_imgs/{animation}'))
            for i in range(num_of_frames):
                p_img = pygame.image.load(os.path.join("images", "players_imgs", animation, f'{i}.png'))
                temp_list.append(p_img)
            animation_list.append(temp_list)
        return animation_list


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_position:tuple):
        pass

class Tile(pygame.sprite.Sprite):
    def __init__(self, start_position:tuple):
        pass