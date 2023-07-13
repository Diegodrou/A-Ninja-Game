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
        self.treshold_gap = 150
        self.CAMERA_SCROLL = 215 #for :unlocked FPS --> 215 30FPS --> 7 60FPS --> 4
        self.treshold_A = self.treshold_gap
        self.treshold_B = width - self.treshold_gap
        self.scroll_amount = 0
        self.locked_A = True #Cause it starts at the right side
        self.locked_B = False
        self.locked = self.locked_A or self.locked_B
    
    #Adds the scroll_value to the x cordinate of  every tile of the map(SE)
    def apply_scroll(self):
        for tile in self.game.all_tiles:
            tile.rect.x += self.game.camera.scroll_amount
    
    #Updates the camera logic(SE)
    def update(self, target):
        self.set_lock_state()
        self.move_camera(target)
        self.apply_scroll()
    
    #Checks if target has crossed the treshold A and if its running towards the treshold
    #->param target is a player object
    #->returns True if both of those condition are met
    def check_if_on_treshold_A(self,target:Player):
        target_left_pos = self.display_px_to_window_px(target.rect.left)
        if target_left_pos <= self.treshold_A and target.moving_left:
            return True
        
        return False
    
    #Checks if target has crossed the treshold B and if its running towards the treshold
    #->param target is a player object
    #->returns True if both of those condition are met
    def check_if_on_treshold_B(self,target:Player):
        target_right_pos = self.display_px_to_window_px(target.rect.right)
        if target_right_pos >= self.treshold_B and target.moving_right:
            return True
        
        return False

    #Moves camera within the game map and sets the scroll amount accordingly(SE)
    #-> param target is the player
    def move_camera(self, target):
        if self.locked:
            self.scroll_amount = 0
            if self.locked_A:
                #self.frame.x = 0
                if self.check_if_on_treshold_B(target):
                    self.scroll_amount = self.game.ceiling(self.CAMERA_SCROLL * self.game.dt)
                    self.scrolling_to_end()
                    self.frame.x += self.scroll_amount
                    self.scroll_amount = -(self.scroll_amount)
            if self.locked_B:
                #self.frame_right = self.MAP.pixelWidth
                if self.check_if_on_treshold_A(target):
                    self.scroll_amount = self.game.ceiling( self.CAMERA_SCROLL * self.game.dt)
                    self.scrolling_to_start()
                    self.frame.x -= self.scroll_amount
                
        else:
            self.scroll_amount = self.game.ceiling(self.CAMERA_SCROLL * self.game.dt)
            on_trA = self.check_if_on_treshold_A(target)
            on_trB = self.check_if_on_treshold_B(target)
            if on_trA:
                self.scrolling_to_start()
                self.frame.x -= self.scroll_amount

            if on_trB:
                self.scrolling_to_end()
                self.frame.x += self.scroll_amount
                self.scroll_amount = -(self.scroll_amount)
        
            if (not on_trA and not on_trB):
                self.scroll_amount = 0
        
    #Decides if the camera is locked or not(SE)
    def set_lock_state(self):
        if self.frame.x <= 0:#locked on side A
            self.locked_A = True
            self.locked_B = False
            self.locked = True
        elif self.frame.right >= self.MAP.pixelWidth:#locked on side B
            self.locked_B = True
            self.locked_A = False
            self.locked = True
        else:#Not locked
            self.locked_A = False
            self.locked_B = False
            self.locked = False
            
    def scrolling_to_end(self):
        if (self.frame.right + self.scroll_amount > self.MAP.pixelWidth):
            self.scroll_amount = self.MAP.pixelWidth - self.frame.right
    
    def scrolling_to_start(self):
        if(self.frame.x - self.scroll_amount < 0 ):
            self.scroll_amount = self.frame.x

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