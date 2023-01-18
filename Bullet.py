import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self,start_position_x, start_position_y ,bullet_direction):
        super().__init__()
        self.image = pygame.Surface((3,2))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center = (start_position_x,start_position_y))
        self.bullet_speed = 3
        self.enemy_direction = bullet_direction

    def update(self,tile_rects,player_rect,scroll):
        #updates Bullet postion
        self.rect.x += self.enemy_direction * self.bullet_speed
        self.rect.x += scroll

        #Checks if the bullet has collided with a rect in the scene
        self.check_for_collisions(tile_rects,player_rect)

    def check_for_collisions(self,tile_rects,player_rect):
        
        if self.rect.colliderect(player_rect):
            self.kill()
        
        for tile in tile_rects:
            if self.rect.colliderect(tile[1]):
                self.kill()


    def draw(self,display):
        display.blit(self.image, (self.rect.x,self.rect.y))
        
