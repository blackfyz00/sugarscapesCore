from registry import register_strategy
from mechanics.movement.findperspectivecell import find_perspective_cell
from mechanics.movement.move import move

@register_strategy("movement")
def movement_strategy(ctx):
    """Движение агентов"""
    grid = ctx["grid"]
    agents_map = ctx["agents_map"]
    
    for agent in list(agents_map.values()):
        if agent["id"] not in agents_map:
            continue
        current_cell = grid[agent["y"]][agent["x"]]
        best_cell = find_perspective_cell(current_cell, grid, agents_map)
        if best_cell:
            move(current_cell, best_cell, agents_map)
