def check_collision(rect, walls):
    for wall in walls:
        if rect.colliderect(wall):
            return True
    return False

def bullet_walls(bullet, walls):
    return check_collision(bullet.rect, walls)

def bullet_tank(bullet, tank):
    return bullet.rect.colliderect(tank.rect)