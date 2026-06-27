from settings import *
import pygame as pg
import math

class Bullet:
    def __init__(self, x, y, angle, owner):
        self.rect = pg.Rect(x - BULLET_SIZE // 2, y - BULLET_SIZE // 2, BULLET_SIZE, BULLET_SIZE)
        rad = math.radians(angle)
        self.vx = math.cos(rad) * BULLET_SPEED
        self.vy = math.sin(rad) * BULLET_SPEED
        self.owner = owner

    def update(self, walls):
        self.rect.x += self.vx
        self.rect.y += self.vy

        for wall in walls:
            if self.rect.colliderect(wall):
                return False
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            return False
        return True

    def is_off_screen(self, screen_width, screen_height):
        return self.rect.bottom < 0 or self.rect.top > screen_height or self.rect.right < 0 or self.rect.left > screen_width
    
    def draw(self, screen):
        pg.draw.rect(screen, COLOR_BULLET, self.rect)
