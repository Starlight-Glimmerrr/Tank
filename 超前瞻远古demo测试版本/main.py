import sys
import os

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发和打包环境"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


from settings import *
from tank import Tank
from bullet import Bullet
from controllers import PlayerController, AIController
from wall import get_walls
from grid import build_grid
import pygame as pg
pg.init()
# 游戏状态
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_VICTORY = 3

game_state = STATE_MENU

# 定义屏幕
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# 定义标题
pg.display.set_caption("Tank")

# 创建地图
walls = get_walls()

# 生成网格
grid = build_grid(walls)

# 创建控制器和坦克
player_ctrl = PlayerController()
player_tank = Tank(80, 780, player_ctrl, COLOR_PLAYER_TANK)
ai_ctrl = AIController(player_tank, grid)
enemy_tank = Tank(1480, 80, ai_ctrl, COLOR_ENEMY_TANK)

# 定义时钟
clock = pg.time.Clock()
# 定义子弹
bullets = []

def reset_game():
    global bullets, player_tank, enemy_tank, player_ctrl, ai_ctrl

    bullets.clear()

    player_tank.rect.x = 80
    player_tank.rect.y = 780

    enemy_tank.rect.x = 1480
    enemy_tank.rect.y = 80

    player_ctrl.shot_cooldown = 0

    ai_ctrl.shot_cooldown = 0
    ai_ctrl.evade_timer = 0
    ai_ctrl.evade_dx = 0
    ai_ctrl.evade_dy = 0

    player_tank.active_bullets = 0
    enemy_tank.active_bullets = 0

def draw_text(screen, text, size, x, y, color = (255, 255, 255)):
    font_path = resource_path(os.path.join("Resource", "Fonts", "字体.ttf"))
    font = pg.font.Font(font_path, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect(center = (x, y))
    screen.blit(surface, rect)
# 主循环  
running = True
while running:
    for ev in pg.event.get():
        # 退出事件
        if ev.type == pg.QUIT:
            running = False
        # 键盘按键事件
        if ev.type == pg.KEYDOWN:
            if game_state == STATE_MENU:
                # 菜单状态：按任意键开始
                game_state = STATE_PLAYING
                reset_game()
            elif game_state in (STATE_GAMEOVER, STATE_VICTORY):
                if ev.key == pg.K_r:
                    game_state = STATE_PLAYING
                    reset_game()
                elif ev.key == pg.K_ESCAPE:
                    running = False
        if game_state == STATE_PLAYING:
            player_ctrl.shot_control(ev, player_tank, bullets)

    if game_state == STATE_PLAYING:

        # 控制
        keys = pg.key.get_pressed()
        mouse_pos = pg.mouse.get_pos()

        player_tank.update(keys = keys, mouse_pos = mouse_pos,walls = walls)
        enemy_tank.update(bullets = bullets, walls = walls)

        # 边界控制
        player_tank.clamp(screen.get_rect())
        enemy_tank.clamp(screen.get_rect())



        # 子弹移动 
        for bullet in bullets[:]:
            if not bullet.update(walls):
                bullet.owner.remove_bullet()
                bullets.remove(bullet)
                continue
            if bullet.rect.colliderect(player_tank.rect) and bullet.owner != player_tank:
                bullet.owner.remove_bullet()
                bullets.remove(bullet)
                print("You are loser……")
                game_state = STATE_GAMEOVER
                continue
            if bullet.rect.colliderect(enemy_tank.rect) and bullet.owner != enemy_tank:
                bullet.owner.remove_bullet()
                bullets.remove(bullet)
                print("You are winner!!!")
                game_state = STATE_VICTORY
                continue

    # 画背景
    screen.fill(COLOR_BG)


    # 画坦克
    player_tank.draw(screen)
    enemy_tank.draw(screen)

    # 画子弹
    for bullet in bullets:
        bullet.draw(screen)

    # 画地图
    for wall in walls:
        pg.draw.rect(screen, COLOR_WALL, wall)

    if game_state == STATE_MENU:

        draw_text(screen, "坦克大战", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, COLOR_FONT)
        draw_text(screen, "按任意键开始", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, COLOR_FONT)
    elif game_state in (STATE_GAMEOVER, STATE_VICTORY):
        if game_state == STATE_GAMEOVER:
            draw_text(screen, "你输了", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, COLOR_FONT)
        else:
            draw_text(screen, "你赢了！", 72, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, COLOR_FONT)
        draw_text(screen, "按 R 重新开始", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, COLOR_FONT)
        draw_text(screen, "按 ESC 退出", 36, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80, COLOR_FONT)    

    # 刷新
    pg.display.flip()

    # 控制帧率
    clock.tick(60)
pg.quit()

### 