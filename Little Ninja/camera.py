import pygame
from map import Map
from sprites import Player

class Camera:
    def __init__(self, width:int, height:int, map:Map, game_attributes, display_size:tuple):
        self.frame = pygame.Rect(0,0, width, height)
        self.game = game_attributes
        self.width = width
        self.height = height
        self.DISPLAY_SIZE = display_size
        self.WINDOW_SIZE = (width,height)
        self.MAP = map
        self.treshold_gap = 100
        self.CAMERA_SCROLL = 1
        self.treshold_A = self.treshold_gap
        self.treshold_B = width - self.treshold_gap

    def apply_scroll(self, entity):
        return entity.rect.move(self.frame.topleft)
    
    #Updates the camera logic(SE)
    def update(self, target):
        self.move_camera(target)
    
    #Checks if target has crossed the treshold A and if its running towards the treshold
    #->param target is a player object
    #->returns True if both of those condition are met
    def check_if_on_treshold_A(self,target:Player):
        target_left_pos = self.display_px_to_window_px(target.rect.left)
        if target_left_pos < self.treshold_A and target.velocity.x < 0:
            return True
        
        return False
    
    #Checks if target has crossed the treshold B and if its running towards the treshold
    #->param target is a player object
    #->returns True if both of those condition are met
    def check_if_on_treshold_B(self,target:Player):
        target_right_pos = self.display_px_to_window_px(target.rect.right)
        if target_right_pos > self.treshold_B and target.velocity.x > 0:
            return True
        
        return False
    
    #Checks if the camera is out of the map
    def out_of_map(self):
        if self.frame.x < 0:
            return True
        
        if self.frame.right > self.MAP.pixelWidth:
            return True
        
        return False

    #Moves camera within the game map
    def move_camera(self, target):
        out_Of_Map = self.out_of_map()
        if self.check_if_on_treshold_A(target) :
            self.frame.x -= self.CAMERA_SCROLL 

            
        if self.check_if_on_treshold_B(target):
            self.frame.x += self.CAMERA_SCROLL
    
    #Converts display pixel x coordinate to window pixel x coordinates
    #-> param n an interger
    #-> return an interger
    def display_px_to_window_px(self,n:int):
        coef = self.WINDOW_SIZE[0] / self.DISPLAY_SIZE[0]
        return int(n * coef)
    
    #Converts window pixel x coordinate to display pixel x coordinates
    #-> param n an interger
    #-> return an interger
    def window_px_to_display_px(self, n:int):
        coef = self.WINDOW_SIZE[0] / self.DISPLAY_SIZE[0]
        return int(n / coef)

    def show_thresholds(self,window):
        pygame.draw.line(window,"YELLOW",(self.treshold_A,0),(self.treshold_A,416))
        pygame.draw.line(window,"YELLOW",(self.treshold_B,0,),(self.treshold_B,416))
