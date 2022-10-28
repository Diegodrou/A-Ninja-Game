from settings import TILE_SIZE
import pygame
from Tile import Tile

class World():
    def __init__(self,game_map):
        # lvl_setup
        self.tile_rects = []    
        self.setup_level(game_map)
        self.scroll = 0

    def setup_level(self,lvl_layout):
        self.tiles = pygame.sprite.Group()
        
        for row_index,row in enumerate(lvl_layout):
            for col_index,cell in enumerate(row):
                if cell != -1 and cell != 1:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    tile = Tile((x,y))
                    self.tiles.add(tile)
        
    def run(self):
        self.tiles.update(0)
        tile_rects = self.tiles
        return tile_rects

    def spawnpoint(self,lvl_layout):
        for row_index,row in enumerate(lvl_layout):
            for col_index,cell in enumerate(row):
                if cell == 1:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    spawn = (x,y)
                    return spawn
    
    def scroll_x(self,world_shift):
        self.tiles.update(world_shift)

    def draw(self,display):
        self.tiles.draw(display)