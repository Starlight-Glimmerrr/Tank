from settings import *
from collision import check_collision
import math
import pygame as pg

class Tank:
    def __init__(self, x, y, controller, color = COLOR_PLAYER_TANK):
        self.rect = pg.Rect(x, y, TANK_SIZE, TANK_SIZE)
        self.color = color
        self.controller = controller
        self.turret_angle = 0
        self.active_bullets = 0

    def update(self, **kwargs):
        self.controller.control(self, **kwargs)

    def clamp(self, screen_rect):
        self.rect.clamp_ip(screen_rect)

    def draw(self, screen):
        pg.draw.rect(screen, self.color, self.rect)

        center = self.rect.center
        rad = math.radians(self.turret_angle)
        length = self.rect.width // 2
        end_x = center[0] + math.cos(rad) * length
        end_y = center[1] + math.sin(rad) * length
        pg.draw.line(screen, (self.color[0] + 50, self.color[1] + 50, self.color[2]), center, (end_x, end_y), TANK_TURRET_WIDTH)

    def try_move(self, dx, dy, walls):
        self.rect.x += dx
        if check_collision(self.rect, walls):
            self.rect.x -= dx
        self.rect.y += dy
        if check_collision(self.rect, walls):
            self.rect.y -= dy    

    def add_bullet(self):
        self.active_bullets += 1

    def remove_bullet(self):
        if self.active_bullets > 0:
            self.active_bullets -= 1