import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self,start_position_x, start_position_y):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (start_position_x,start_position_y))
        self.bullet_speed = 5

    def update(self,enemy_direction):
        self.rect.x += enemy_direction * self.bullet_speed

        #if self.rect.colliderect():
            #self.kill()

    def draw(self,display):
        display.blit(self.image, (self.rect.x,self.rect.y))
        
