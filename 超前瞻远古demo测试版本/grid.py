from settings import *
def build_grid(walls):
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    for wall in walls:
        gx = wall.x // TEMP_GRID_SIZE
        gy = wall.y // TEMP_GRID_SIZE

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    grid[ny][nx] = 1
    return grid