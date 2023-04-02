from settings import TILE_SIZE, tiles_imgs
import pygame


class World():
    def __init__(self,game_map):
        # lvl_setup
        self.tile_rects = []    
        self.setup_level(game_map)
        self.scroll = 0

        #Size of the map in tiles
        self.world_tile_width = len(game_map[0])
        self.world_tile_height = len(game_map)
        
        #Size of the map in pixels
        self.world_pixel_size = (self.world_tile_width * TILE_SIZE, self.world_tile_height * TILE_SIZE)


    def setup_level(self,lvl_layout):
        
        for row_index,row in enumerate(lvl_layout):
            for col_index,cell in enumerate(row):
                if cell >= 0 and cell != 1 and cell != 2:
                    img = tiles_imgs[cell]
                    img_rect = img.get_rect()
                    img_rect.x = col_index * TILE_SIZE
                    img_rect.y = row_index * TILE_SIZE
                    tile_data = (img, img_rect)
                    if cell >=0 and cell <1:
                        self.tile_rects.append(tile_data) 

        
    def run(self):
        return self.tile_rects

    def spawnpoint(self,lvl_layout):
        for row_index,row in enumerate(lvl_layout):
            for col_index,cell in enumerate(row):
                if cell == 1:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    spawn = (x,y)
                    return spawn
    def enemy_spawn(self,lvl_layout):
        spawns = []
        for row_index,row in enumerate(lvl_layout):
            for col_index,cell in enumerate(row):
                if cell == 2:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    spawn = (x,y)
                    spawns.append(spawn)
        return spawns
    


    def draw(self,display,screenscroll):
        for tile in self.tile_rects:
            tile[1][0] += screenscroll
            display.blit(tile[0],tile[1])