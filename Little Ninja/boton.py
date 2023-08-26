import pygame

class Boton():
    def __init__(self, x, y, image, scale):
        img_width = image.get_width()
        img_height = image.get_height()
        self.image = pygame.transform.scale(image, (int(img_width*scale), int(img_height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def check_click(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True 

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action
    
    def draw(self,display):
        display.blit(self.image, (self.rect.x, self.rect.y))

class CheckBox():
    def __init__(self, x, y,empty_check_box_image:pygame.Surface, filled_check_box_image:pygame.Surface,state:bool,scale:float):
        empty_img_width = empty_check_box_image.get_width()
        empty_img_height = empty_check_box_image.get_height()
            
        filled_img_width = filled_check_box_image.get_width()
        filled_img_height = filled_check_box_image.get_height()
            
        self.empty_image = pygame.transform.scale(empty_check_box_image, (int(empty_img_width * scale), int(empty_img_height * scale)))
        self.filled_image = pygame.transform.scale(filled_check_box_image,(int(filled_img_width * scale), int(filled_img_height * scale)))
        self.rect = self.empty_image.get_rect()
        self.rect.topleft = (x,y)

        self.clicked = False
        self.state = state

    def check_clicked(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.state = not self.state
                action = True

                
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action
            
    def draw(self,display):
        if self.state == True:
            display.blit(self.filled_image,(self.rect.x, self.rect.y))
        else:
            display.blit(self.empty_image, (self.rect.x, self.rect.y))