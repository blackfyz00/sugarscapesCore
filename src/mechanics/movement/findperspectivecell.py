import math
import random
from utils.welfare_cobb import calculate_welfare_cobb_douglas
from utils.get_neighbors import get_neighbors

def calculate_welfare_for_move(agent: dict, cell: dict) -> float:
    """
    Книжная логика: Cobb-Douglas Welfare Function.
    Считает потенциальное благосостояние, если агент перейдет в эту клетку.
    """
    potential_sugar = agent["sugar"] + cell["sugar"]
    potential_spicy = agent["spicy"] + cell["spicy"]
    return calculate_welfare_cobb_douglas(
        potential_sugar, 
        potential_spicy, 
        agent["sugarm"], 
        agent["spicym"]
    )

def find_perspective_cell(current_cell: dict, map_matrix: list[list[dict]], 
                          agents_map: dict, **kwargs) -> dict | None:
    """
    1. Найти все свободные клетки (включая текущую!) в радиусе зрения (vis).
    2. Вычислить Welfare для каждой и найти глобально лучшую цель.
    3. Если лучшая цель — текущая клетка, остаться на месте.
    4. Иначе выбрать соседа, ведущего к цели.
    """
    agent_id = current_cell.get("agent_id")
    if agent_id is None:
        return None
    agent = agents_map[agent_id]
    cx, cy = current_cell["x"], current_cell["y"]
    vis = agent["vis"]  
    
    perspective_cells = []
    
    max_y = len(map_matrix)
    max_x = len(map_matrix[0]) if max_y > 0 else 0
    
    start_y = max(0, cy - vis)
    end_y = min(max_y, cy + vis + 1)
    
    start_x = max(0, cx - vis)
    end_x = min(max_x, cx + vis + 1)
    
    current_welfare = calculate_welfare_for_move(agent, current_cell)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if x == cx and y == cy:
                continue
                
            cell = map_matrix[y][x]
            
            if cell["agent_id"] is not None:
                continue
                
            dist = math.sqrt((cell["x"] - cx)**2 + (cell["y"] - cy)**2)
            if dist <= vis:
                perspective_cells.append((cell, dist))
                
    candidates_with_welfare = []
    for cell, dist in perspective_cells:
        w = calculate_welfare_for_move(agent, cell)
        candidates_with_welfare.append({"cell": cell, "welfare": w, "dist": dist})
        
    if not candidates_with_welfare:
        return None

    max_external_welfare = max(item["welfare"] for item in candidates_with_welfare)
    
    if current_welfare > max_external_welfare or math.isclose(current_welfare, max_external_welfare, rel_tol=1e-5):
        return current_cell
        
    best_targets = [
        item for item in candidates_with_welfare 
        if math.isclose(item["welfare"], max_external_welfare, rel_tol=1e-5)
    ]
    
    min_dist_to_target = min(item["dist"] for item in best_targets)
    closest_best_targets = [
        item["cell"] for item in best_targets 
        if math.isclose(item["dist"], min_dist_to_target, rel_tol=1e-5)
    ]
    
    target_cell = random.choice(closest_best_targets)

    # Если цель на расстоянии 1 шага, идем туда напрямую
    direct_dist = math.sqrt((target_cell["x"] - cx)**2 + (target_cell["y"] - cy)**2)
    if direct_dist <= 1.5:
        return target_cell

    # Иначе делаем промежуточный шаг через get_neighbors
    neighbors = get_neighbors(current_cell, map_matrix)
    free_neighbors = [n for n in neighbors if n["agent_id"] is None]
    
    if not free_neighbors:
        return current_cell  # Если идти некуда, стоим на месте

    best_neighbor = min(
        free_neighbors,
        key=lambda n: math.sqrt((n["x"] - target_cell["x"])**2 + (n["y"] - target_cell["y"])**2)
    )
    
    return best_neighbor
