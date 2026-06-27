import pygame as pg
from settings import WALL_SIZE, COLOR_WALL
from map_data import LEVEL_01

def get_walls():
    walls = []
    for y, row in enumerate(LEVEL_01):
        for x, cell in enumerate(row):
            if cell == 1:
                walls.append(pg.Rect(x * WALL_SIZE, y * WALL_SIZE, WALL_SIZE, WALL_SIZE))
    return walls