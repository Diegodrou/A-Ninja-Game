import pygame
from settings import *

class Map:
    def __init__(self,level_layout):
        self.data = level_layout

        #Width and Height of the map in tiles:
        
        self.tileWidth = len(level_layout[0])
        self.tileHeight = len(level_layout)
        
        #Width and Heigh of the map in pixels:

        self.pixelWidth = self.tileWidth * TILE_SIZE
        self.pixelHeight = self.tileHeight * TILE_SIZE