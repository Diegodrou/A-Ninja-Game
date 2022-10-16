import pygame
import os
FPS = 75
game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','1','1','1','1','1','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]

#Asset Loading
brick_tile = pygame.image.load(r'assets/img/brick.png')
city_background = pygame.image.load(r'assets/img/background.png')
menu_background = pygame.image.load('assets/menu/0.png')
resume_b_img = pygame.image.load('assets/img/menu_b/button_resume.png')
quit_b_img = pygame.image.load('assets/img/menu_b/button_quit.png')
options_b_img = pygame.image.load('assets/img/menu_b/button_options.png')
#Loads all frames of the background animation
menu_bimages = []
num_of_frames = len(os.listdir(f'assets/menu'))
for i in range(num_of_frames):
    b_img = pygame.image.load(f'assets/menu/{i}.png')
    menu_bimages.append(b_img)



#Options
TILE_SIZE = brick_tile.get_width()
WINDOW_HEIGHT = 416
WINDOW_WIDTH = 600
DISPLAY_SIZE = (300,208)
WINDOW_SIZE = (WINDOW_WIDTH,WINDOW_HEIGHT)
