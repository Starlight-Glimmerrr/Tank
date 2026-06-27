import pygame as pg
import math
from abc import ABC, abstractmethod
from settings import *
from bullet import Bullet
from 算法.A_star import *
from collision import check_collision
class Controller(ABC):
    @abstractmethod
    def control(self, tank, **kwargs):
        pass

class PlayerController(Controller):
    def __init__(self):
        self.shot_cooldown = 0

    def control(self, tank, **kwargs):
        self.update_cooldown()
        self.move_control(tank, keys = kwargs.get('keys'), mouse_pos = kwargs.get('mouse_pos'), walls = kwargs.get('walls'))
        
    def shot_control(self, event, tank, bullets):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.shot_cooldown == 0 and tank.active_bullets < BULLET_NUMBER:
            new_bullet = Bullet(tank.rect.centerx, tank.rect.centery, tank.turret_angle, tank)
            bullets.append(new_bullet)
            tank.add_bullet()
            self.shot_cooldown = PLAYER_SHOT_DELAY

    def update_cooldown(self):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1


    def move_control(self, tank, keys = None, mouse_pos = None, walls = None):
        dx = 0
        dy = 0
        
        if keys:
            if keys[pg.K_a]: 
                dx = -TANK_SPEED
            if keys[pg.K_d]: 
                dx = TANK_SPEED
            if keys[pg.K_w]: 
                dy = -TANK_SPEED
            if keys[pg.K_s]: 
                dy = TANK_SPEED
        if dx != 0 or dy != 0:
            tank.try_move(dx, dy, walls)
        if mouse_pos:
            dx = mouse_pos[0] - tank.rect.centerx
            dy = mouse_pos[1] - tank.rect.centery
            tank.turret_angle = math.degrees(math.atan2(dy, dx))

class AIController(Controller):
    def __init__(self, player_tank,grid):
        self.player = player_tank
        self.grid = grid
        self.path = []
        self.path_timer = 0
        self.shot_cooldown = 0
        self.evade_dx = 0          # 水平闪避方向
        self.evade_dy = 0          # 垂直闪避方向
        self.evade_timer = 0
        self.evade_speed = EVADE_SPEED   # 添加这一行

    
    def control(self, tank, bullets=None, walls=None, **kwargs):
        # ===== 闪避逻辑（最高优先级） =====
        # 持续闪避状态
        if self.evade_timer > 0:
            self.evade_timer -= 1
            tank.try_move(self.evade_dx * self.evade_speed, self.evade_dy * self.evade_speed, walls)
            return

        # 检测威胁子弹
        if bullets is not None:
            for bullet in bullets:
                if bullet.owner == tank:
                    continue

                # 计算子弹到坦克的方向向量
                to_tank_x = tank.rect.centerx - bullet.rect.centerx
                to_tank_y = tank.rect.centery - bullet.rect.centery

                speed = (bullet.vx**2 + bullet.vy**2) ** 0.5
                if speed == 0:
                    continue
                bullet_dir_x = bullet.vx / speed
                bullet_dir_y = bullet.vy / speed

                dot = to_tank_x * bullet_dir_x + to_tank_y * bullet_dir_y
                if dot < 0:
                    continue

                cross = to_tank_x * bullet_dir_y - to_tank_y * bullet_dir_x
                if abs(cross) > 30:
                    continue

                dist = (to_tank_x**2 + to_tank_y**2) ** 0.5
                if dist > 250:
                    continue

                # === 根据子弹角度选择闪避方向 ===
                bullet_angle = math.degrees(math.atan2(bullet.vy, bullet.vx)) % 360

                is_horizontal = (bullet_angle < 45 or bullet_angle > 315 or (180 - 45 < bullet_angle < 180 + 45))
                is_vertical = (90 - 45 < bullet_angle < 90 + 45 or 270 - 45 < bullet_angle < 270 + 45)

                if is_horizontal:
                    def get_vertical_space(dy, tank, walls, max_steps=20):
                        for step in range(1, max_steps + 1):
                            test_rect = tank.rect.copy()
                            test_rect.y += dy * step
                            if check_collision(test_rect, walls):
                                return step - 1
                        return max_steps

                    up_space = get_vertical_space(-self.evade_speed, tank, walls)
                    down_space = get_vertical_space(self.evade_speed, tank, walls)

                    if up_space > 0 or down_space > 0:
                        evade_dy = -self.evade_speed if up_space >= down_space else self.evade_speed
                        self.evade_dx = 0
                        self.evade_dy = 1 if evade_dy > 0 else -1
                        self.evade_timer = 20
                        tank.try_move(0, evade_dy, walls)
                        return

                elif is_vertical:
                    def get_horizontal_space(dx, tank, walls, max_steps=20):
                        for step in range(1, max_steps + 1):
                            test_rect = tank.rect.copy()
                            test_rect.x += dx * step
                            if check_collision(test_rect, walls):
                                return step - 1
                        return max_steps

                    left_space = get_horizontal_space(-self.evade_speed, tank, walls)
                    right_space = get_horizontal_space(self.evade_speed, tank, walls)

                    if left_space > 0 or right_space > 0:
                        evade_dx = -self.evade_speed if left_space >= right_space else self.evade_speed
                        self.evade_dx = 1 if evade_dx > 0 else -1
                        self.evade_dy = 0
                        self.evade_timer = 20
                        tank.try_move(evade_dx, 0, walls)
                        return

        # ===== 寻路和移动逻辑（不变） =====
        self.path_timer -= 1
        if self.path_timer <= 0 or not self.path:
            self.path_timer = 30
            start = (tank.rect.centerx // TEMP_GRID_SIZE, tank.rect.centery // TEMP_GRID_SIZE)
            goal = (self.player.rect.centerx // TEMP_GRID_SIZE, self.player.rect.centery // TEMP_GRID_SIZE)
            self.path = a_star(self.grid, start, goal)
            if self.path:
                self.path.pop(0)

        if self.path:
            next_grid = self.path[0]
            target_px = next_grid[0] * TEMP_GRID_SIZE + TEMP_GRID_SIZE // 2
            target_py = next_grid[1] * TEMP_GRID_SIZE + TEMP_GRID_SIZE // 2
            dx = 0
            dy = 0
            if target_px > tank.rect.centerx:
                dx = ENEMY_SPEED
            elif target_px < tank.rect.centerx:
                dx = -ENEMY_SPEED
            if target_py > tank.rect.centery:
                dy = ENEMY_SPEED
            elif target_py < tank.rect.centery:
                dy = -ENEMY_SPEED
            if dx != 0 or dy != 0:
                tank.try_move(dx, dy, walls)
            if abs(tank.rect.centerx - target_px) < 10 and abs(tank.rect.centery - target_py) < 10:
                self.path.pop(0)
        else:
            dx = 0
            dy = 0
            if self.player.rect.centerx > tank.rect.centerx:
                dx = ENEMY_SPEED
            elif self.player.rect.centerx < tank.rect.centerx:
                dx = -ENEMY_SPEED
            if self.player.rect.centery > tank.rect.centery:
                dy = ENEMY_SPEED
            elif self.player.rect.centery < tank.rect.centery:
                dy = -ENEMY_SPEED
            if dx != 0 or dy != 0:
                tank.try_move(dx, dy, walls)

        dx = self.player.rect.centerx - tank.rect.centerx
        dy = self.player.rect.centery - tank.rect.centery
        tank.turret_angle = math.degrees(math.atan2(dy, dx))

        # === 射击逻辑（瞄准 + 视线检测） ===
        if self.shot_cooldown <= 0:
            # 1. 角度判断：炮管是否对准玩家
            ideal_angle = math.degrees(math.atan2(
                self.player.rect.centery - tank.rect.centery,
                self.player.rect.centerx - tank.rect.centerx
            ))
            angle_diff = abs(ideal_angle - tank.turret_angle)
            # 归一化到 0~180
            angle_diff = min(angle_diff, 360 - angle_diff)

            if angle_diff < 20:  # 20° 以内
                # 2. 视线检测：中间是否有墙
                # 从 AI 到玩家方向，每隔 10 像素检测一次
                dx = self.player.rect.centerx - tank.rect.centerx
                dy = self.player.rect.centery - tank.rect.centery
                dist = (dx**2 + dy**2) ** 0.5
                step = 10
                blocked = False
                for t in range(0, int(dist), step):
                    check_x = tank.rect.centerx + dx * t / dist
                    check_y = tank.rect.centery + dy * t / dist
                    check_rect = pg.Rect(check_x - 2, check_y - 2, 4, 4)
                    for wall in walls:
                        if check_rect.colliderect(wall):
                            blocked = True
                            break
                    if blocked:
                        break
                if not blocked:
                    # 开火！
                    bullets.append(Bullet(tank.rect.centerx, tank.rect.centery, tank.turret_angle, owner=tank))
                    self.shot_cooldown = ENEMY_SHOT_DELAY
        else:
            self.shot_cooldown -= 1