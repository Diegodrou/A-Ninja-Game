import pygame
import os
import pickle

FPS = 75
# Asset Loading
# loads the game levels
lvls = []
for i in range(0, 6):
    pickle_in = open(f'Levels/level{i}_data', 'rb')
    lvl = pickle.load(pickle_in)
    lvls.append(lvl)
# Loads tiles images
tiles_imgs = []
num_tiles_imgs = len(os.listdir(f'assets/img/tiles'))
for x in range(num_tiles_imgs):
    tile_i = pygame.image.load(f'assets/img/tiles/{x}.png')
    tiles_imgs.append(tile_i)


# loads background images
bg_layers = []
for i in range(2,5):
    layer = pygame.image.load(f"assets/img/background_layers/background_{i}.png")
    bg_layers.append(layer)

#
#blue_background = pygame.image.load('assets/img/background_0.png')
SKY = pygame.image.load("assets/img/background_0.png")
sunCloud = pygame.image.load("assets/img/background_1.png")
#SKY.blit(sunCloud,(0,0))

menu_background = pygame.image.load('assets/menu/0.png')
resume_b_img = pygame.image.load('assets/img/menu_b/button_resume.png')
quit_b_img = pygame.image.load('assets/img/menu_b/button_quit.png')
options_b_img = pygame.image.load('assets/img/menu_b/button_options.png')
lvl_1_b_img = pygame.image.load('assets/img/menu_b/level_1.png')
back_b_img = pygame.image.load('assets/img/menu_b/button_back.png')

# Loads all frames of the background animation
menu_bimages = []
num_of_frames = len(os.listdir(f'assets/menu'))
for i in range(num_of_frames):
    b_img = pygame.image.load(f'assets/menu/{i}.png')
    menu_bimages.append(b_img)


# Options
TILE_SIZE = tiles_imgs[0].get_width()
WINDOW_HEIGHT = 416
WINDOW_WIDTH = 600
DISPLAY_SIZE = (300, 208)
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
