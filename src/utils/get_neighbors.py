def get_neighbors(cell, grid):
    x, y = cell["x"], cell["y"]
    neighbors = []
    
    directions = [
        (0, 1), (0, -1), (1, 0), (-1, 0),  # Прямые
        (1, 1), (1, -1), (-1, 1), (-1, -1) # Диагонали
    ]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            neighbors.append(grid[ny][nx])
            
    return neighbors
