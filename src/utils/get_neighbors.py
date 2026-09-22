def get_neighbors(cell, grid):
    x, y = cell["posx"], cell["posy"]
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            neighbors.append(grid[ny][nx])
    return neighbors