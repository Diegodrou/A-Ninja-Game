import pygame

class Button():
    def __init__(self, x, y, image, scale):
        img_width = image.get_width()
        img_height = image.get_height()
        self.image = pygame.transform.scale(image, (int(img_width*scale), int(img_height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

#draws button on screen
    def draw(self,display):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True 

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        display.blit(self.image, (self.rect.x, self.rect.y))

        return action