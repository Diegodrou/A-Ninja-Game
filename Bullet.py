import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self,start_position_x, start_position_y ,bullet_direction):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (start_position_x,start_position_y))
        self.bullet_speed = 5
        self.enemy_direction = bullet_direction

    def update(self):
        self.rect.x += self.enemy_direction * self.bullet_speed

        #if self.rect.colliderect():
            #self.kill()

    def draw(self,display):
        display.blit(self.image, (self.rect.x,self.rect.y))
        
