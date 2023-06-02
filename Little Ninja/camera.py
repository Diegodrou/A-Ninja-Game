import pygame
from settings import window_width

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0,0, width, height)
        self.width = width
        self.height = height
        self.treshold_gap = 100
        self.treshold_A = self.treshold_gap
        self.treshold_B = width - self.treshold_gap

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    
    def update(self, target):
        pass
    
    def check_if_on_treshold(self,target):
        if target.rect.left < self.treshold_A and self.target.velocity.x < 0:
            return True
        
        if target.rect.right > self.treshold_B and self.target.velocity.x > 0:
            return True
        
        return False
    
    def move_map(self,on_treshold, entity):
        if on_treshold:
            pass
