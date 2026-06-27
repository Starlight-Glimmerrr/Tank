import heapq

def get_neighbors(grid, node):
    """
    传入网格和当前节点坐标，返回所有能走的邻居坐标
    """
    x, y = node
    height = len(grid)
    width = len(grid[0])
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    neighbors = []

    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy

        if 0 <= new_x < width and 0 <= new_y < height:
            if grid[new_y][new_x] == 0:
                neighbors.append((new_x, new_y))
    return neighbors

def heuristic(node, goal):
    """
    求曼哈顿距离，也就是当前格子到终点的横向格子数+纵向格子数
    """
    x1, y1 = node
    x2, y2 = goal
    return abs(x1 - x2) + abs(y1 - y2)


def a_star(grid, start, goal):
    came_from = {} 
    g_score = {}
    g_score[start] = 0 # 起点到该点需要多少步
    f_score = {}
    f_score[start] = heuristic(start, goal) # 到该点的预估总代价，g + h
    open_set = [] # 待处理结点
    counter = 0
    heapq.heappush(open_set, (f_score[start], counter, start))
    counter += 1

    closed_set = set()

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        closed_set.add(current)

        for neighbor in get_neighbors(grid, current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)

                heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                counter += 1

    return None
            