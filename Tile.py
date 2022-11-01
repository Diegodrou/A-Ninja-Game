import pygame
from settings import*

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        
        self.rect = self.image.get_rect(topleft = pos)

    def update(self, scroll):
        self.rect.x += scroll